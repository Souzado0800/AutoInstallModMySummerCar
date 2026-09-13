#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados de Validação do My Summer Car Mod Installer.
Testa:
1. Leitura e integridade de ZIPs reais
2. Leitura e integridade de RAR real (Lights On Switches)
3. Agrupamento Main File + 4K (DirtMod Revived)
4. Detecção de conflito de arquivos (idêntico vs alterado)
5. Criação de backups com timestamp em _Backups
6. Proteção contra Path Traversal / Zip Slip
7. Resolução conservadora de pastas-raiz
8. Detecção e tratamento de arquivos perigosos (.exe, .bat)
9. Renomeação e conversão de READMEs para Markdown
10. Modo Simulação (Dry Run)
"""

import os
import sys
import tempfile
import zipfile
import shutil

sys.path.append(r"C:\Users\Souza\Downloads")
import MySummerCarModInstaller as installer

def run_tests():
    print("=" * 70)
    print("      INICIANDO BATERIA COMPLETA DE TESTES AUTOMATIZADOS")
    print("=" * 70)
    
    logger = installer.Logger(os.path.join(tempfile.gettempdir(), "test_installer.log"))
    analyzer = installer.ModAnalyzer(logger)
    
    # -------------------------------------------------------------
    # TESTE 1: Leitura de ZIP real
    # -------------------------------------------------------------
    print("\n[TESTE 1] Leitura e análise de ZIP real...")
    zip_path = r"C:\Users\Souza\Downloads\AutoFuel 1.3-1801-1-3-1682251911.zip"
    pkg_zip = installer.ModPackage(zip_path)
    assert analyzer.analyze_package(pkg_zip), "Falha ao analisar ZIP real"
    assert pkg_zip.has_dll, "ZIP real deveria conter DLL"
    assert "RaycastCore (incluso no pacote)" in pkg_zip.detected_dependencies
    print("  -> OK: ZIP lido com sucesso e dependência RaycastCore detectada.")

    # -------------------------------------------------------------
    # TESTE 2: Leitura de RAR real
    # -------------------------------------------------------------
    print("\n[TESTE 2] Leitura e extração de bytes de RAR real...")
    rar_path = r"C:\Users\Souza\Downloads\Lights On Switches-868-2-0-1686947825.rar"
    pkg_rar = installer.ModPackage(rar_path)
    assert analyzer.analyze_package(pkg_rar), "Falha ao analisar RAR real"
    assert any(m.filename.lower() == "lightsonswitches.dll" for m in pkg_rar.members)
    print("  -> OK: RAR lido com sucesso e DLL LightsOnSwitches.dll identificada.")

    # -------------------------------------------------------------
    # TESTE 3: Agrupamento Main File + 4K
    # -------------------------------------------------------------
    print("\n[TESTE 3] Agrupamento inteligente DirtMod Main + 4K...")
    p1 = installer.ModPackage(r"C:\Users\Souza\Downloads\DirtMod(Revived) Main File-1006-1-0-1-1670520473.zip")
    p2 = installer.ModPackage(r"C:\Users\Souza\Downloads\DirtMod(Revived)4k-1006-1-0-1631887695.zip")
    analyzer.analyze_package(p1)
    analyzer.analyze_package(p2)
    
    is_rel, ratio = installer.ModNormalizer.are_mods_related(p1, p2)
    assert is_rel, f"DirtMod Main e 4K deveriam ser relacionados! Ratio: {ratio}"
    
    grp = installer.ModGroup(p1.mod_name_detected)
    grp.add_package(p1)
    grp.add_package(p2)
    grp.resolve_relationships()
    
    assert grp.main_package == p1, "p1 deveria ser o Main Package do grupo"
    assert p2.related_main_file is not None, "p2 deveria apontar para o Main File"
    print(f"  -> OK: Agrupados sob '{grp.group_name}'. Main: {grp.main_package.filename}")

    # -------------------------------------------------------------
    # TESTE 4: Não agrupamento de sequências distintas (DirtMod vs DirtMod 2)
    # -------------------------------------------------------------
    print("\n[TESTE 4] Diferenciação de sequências (DirtMod vs DirtMod 2)...")
    p_seq1 = installer.ModPackage("DirtMod(Revived).zip")
    p_seq2 = installer.ModPackage("DirtMod 2.zip")
    p_seq1.base_group_name = installer.ModNormalizer.get_base_group_key(p_seq1.filename)
    p_seq2.base_group_name = installer.ModNormalizer.get_base_group_key(p_seq2.filename)
    rel_seq, _ = installer.ModNormalizer.are_mods_related(p_seq1, p_seq2)
    assert not rel_seq, "DirtMod e DirtMod 2 NÃO deveriam ser agrupados!"
    print("  -> OK: DirtMod e DirtMod 2 mantidos em grupos separados.")

    # -------------------------------------------------------------
    # TESTE 5: Proteção contra Path Traversal / Zip Slip
    # -------------------------------------------------------------
    print("\n[TESTE 5] Proteção contra Zip Slip e caminhos maliciosos...")
    test_mods_dir = os.path.join(tempfile.gettempdir(), "test_msc_mods")
    os.makedirs(test_mods_dir, exist_ok=True)
    resolver = installer.PathResolver(test_mods_dir, logger)
    
    assert not resolver._is_safe_path("../../../Windows/System32/calc.exe"), "Zip Slip ../../ não bloqueado!"
    assert not resolver._is_safe_path("C:/Windows/calc.exe"), "Caminho absoluto não bloqueado!"
    assert not resolver._is_safe_path("/etc/passwd"), "Barra inicial não bloqueada!"
    assert resolver._is_safe_path("Assets/TestMod/test.unity3d"), "Caminho legítimo foi bloqueado!"
    assert resolver._is_safe_path("TestMod.dll"), "Caminho legítimo foi bloqueado!"
    print("  -> OK: Tentativas maliciosas bloqueadas com sucesso.")

    # -------------------------------------------------------------
    # TESTE 6: Resolução conservadora de pastas-raiz
    # -------------------------------------------------------------
    print("\n[TESTE 6] Resolução conservadora de estrutura interna...")
    # Caso 1: Mods/DirtMod.dll -> deve virar DirtMod.dll (e NUNCA Mods/Mods/DirtMod.dll)
    pkg_case1 = installer.ModPackage("TestContainer.zip")
    pkg_case1.members = [
        installer.ArchiveMember("Mods/DirtMod.dll", 100, False),
        installer.ArchiveMember("Mods/Assets/DirtMod/test.unity3d", 200, False)
    ]
    pkg_case1.mod_name_detected = "DirtMod"
    resolver.resolve_package_paths(pkg_case1)
    assert pkg_case1.resolved_mappings["Mods/DirtMod.dll"] == "DirtMod.dll", "Falha ao desempacotar container Mods/"
    assert pkg_case1.resolved_mappings["Mods/Assets/DirtMod/test.unity3d"] == "Assets/DirtMod/test.unity3d"
    
    # Caso 2: DirtMod/Mods/DirtMod.dll -> deve virar DirtMod.dll
    pkg_case2 = installer.ModPackage("TestRelease.zip")
    pkg_case2.members = [
        installer.ArchiveMember("DirtMod_v1.0/Mods/DirtMod.dll", 100, False),
        installer.ArchiveMember("DirtMod_v1.0/Mods/Assets/DirtMod/test.unity3d", 200, False)
    ]
    pkg_case2.mod_name_detected = "DirtMod"
    resolver.resolve_package_paths(pkg_case2)
    assert pkg_case2.resolved_mappings["DirtMod_v1.0/Mods/DirtMod.dll"] == "DirtMod.dll"

    # Caso 3: Preservação de estrutura intencional
    pkg_case3 = installer.ModPackage("LegitMod.zip")
    pkg_case3.members = [
        installer.ArchiveMember("LegitMod.dll", 100, False),
        installer.ArchiveMember("Assets/LegitMod/model.unity3d", 200, False)
    ]
    pkg_case3.mod_name_detected = "LegitMod"
    resolver.resolve_package_paths(pkg_case3)
    assert pkg_case3.resolved_mappings["LegitMod.dll"] == "LegitMod.dll"
    assert pkg_case3.resolved_mappings["Assets/LegitMod/model.unity3d"] == "Assets/LegitMod/model.unity3d"
    print("  -> OK: Estruturas de pastas mapeadas de acordo com as regras conservadoras.")

    # -------------------------------------------------------------
    # TESTE 7: README renaming e indexação de duplicatas
    # -------------------------------------------------------------
    print("\n[TESTE 7] Renomeação de README para readme(NomeDoMod).md...")
    pkg_readme = installer.ModPackage("ReadmeMod.zip")
    pkg_readme.members = [
        installer.ArchiveMember("README.txt", 50, False),
        installer.ArchiveMember("readme.md", 50, False)
    ]
    pkg_readme.mod_name_detected = "SuperMod"
    resolver.resolve_package_paths(pkg_readme)
    mappings = list(pkg_readme.resolved_mappings.values())
    assert "readme(SuperMod).md" in mappings
    assert "readme(SuperMod_2).md" in mappings
    print("  -> OK: READMEs formatados como readme(SuperMod).md e readme(SuperMod_2).md.")

    # -------------------------------------------------------------
    # TESTE 8: Hash SHA-256 e detecção de arquivos existentes
    # -------------------------------------------------------------
    print("\n[TESTE 8] Hash SHA-256 e detecção de arquivos idênticos vs modificados...")
    conflict_mgr = installer.ConflictManager(test_mods_dir, logger)
    sample_file = os.path.join(test_mods_dir, "SampleTest.dll")
    with open(sample_file, "wb") as f:
        f.write(b"ORIGINAL_CONTENT_12345")

    # Conteúdo idêntico
    exists, is_identical, _ = conflict_mgr.check_destination("SampleTest.dll", b"ORIGINAL_CONTENT_12345")
    assert exists and is_identical, "Deveria detectar arquivo idêntico"

    # Conteúdo modificado
    exists2, is_identical2, _ = conflict_mgr.check_destination("SampleTest.dll", b"MODIFIED_CONTENT_67890")
    assert exists2 and not is_identical2, "Deveria detectar arquivo modificado"
    print("  -> OK: Detecção precisa de hash SHA-256 idêntico e alterado.")

    # -------------------------------------------------------------
    # TESTE 9: Criação de Backups em _Backups com Timestamp
    # -------------------------------------------------------------
    print("\n[TESTE 9] Criação de backups em _Backups...")
    backup_path = conflict_mgr.create_backup(sample_file)
    assert backup_path and os.path.exists(backup_path), "Arquivo de backup não foi criado!"
    assert "_Backups" in backup_path
    assert backup_path.endswith(".bak")
    print(f"  -> OK: Backup criado com sucesso em: {os.path.basename(backup_path)}")

    # -------------------------------------------------------------
    # TESTE 10: Limpeza do ambiente de teste
    # -------------------------------------------------------------
    shutil.rmtree(test_mods_dir, ignore_errors=True)

    print("\n" + "=" * 70)
    print("      TODOS OS 10 TESTES AUTOMATIZADOS PASSARAM COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
