#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suíte de Testes da Auditoria Final:
- Roteamento dinâmico de pastas de assets sem prefixo Assets/
- Roteamento de textura solta na raiz para pasta de assets correspondente
- Isolamento seguro de colisões entre mods distintos (preservação do mod existente)
- Compartilhamento de dependências idênticas entre mods sem conflito
- Segurança de numeração de READMEs sem colisões
"""

import os
import sys
import tempfile
import zipfile
import shutil

sys.path.append(r"C:\Users\Souza\Downloads")
import MySummerCarModInstaller as installer

def run_audit_tests():
    print("=" * 70)
    print("   BATERIA ESPECÍFICA DA AUDITORIA FINAL - REGRAS GENERALISTAS")
    print("=" * 70)

    test_dir = os.path.join(tempfile.gettempdir(), "test_audit_generalist")
    test_downloads = os.path.join(test_dir, "Downloads")
    test_mods = os.path.join(test_dir, "Mods")
    os.makedirs(test_downloads, exist_ok=True)
    os.makedirs(test_mods, exist_ok=True)

    logger = installer.Logger(os.path.join(test_downloads, "audit_test.log"))
    mem_db = installer.ModMemoryDatabase(test_downloads, logger)
    path_resolver = installer.PathResolver(test_mods, logger, mem_db)
    auto_inst = installer.AutoInstaller(test_mods, mem_db, logger)

    def make_zip(zip_name, files_dict):
        zp = os.path.join(test_downloads, zip_name)
        with zipfile.ZipFile(zp, "w") as zf:
            for fname, content in files_dict.items():
                zf.writestr(fname, content)
        return zp

    # -------------------------------------------------------------
    # TESTE A: ZIP com pasta de assets mas sem 'Assets/' e sem 'Mods/'
    # Exemplo: TexturesPack/custom_car.png (sem DLL)
    # -------------------------------------------------------------
    print("\n[TESTE A] ZIP com subpasta de assets sem prefixo Assets/...")
    # Criar pasta existente em Mods/Assets/CustomCar para simular mod instalado
    os.makedirs(os.path.join(test_mods, "Assets", "CustomCar"), exist_ok=True)
    
    z_asset = make_zip("CustomCar_Textures.zip", {
        "CustomCar/body_texture.png": b"BODY_PNG_DATA",
        "CustomCar/interior.unity3d": b"INTERIOR_DATA"
    })
    pkg_asset = installer.ModPackage(z_asset)
    analyzer = installer.ModAnalyzer(logger)
    analyzer.analyze_package(pkg_asset)
    path_resolver.resolve_package_paths(pkg_asset)
    
    assert "Assets/CustomCar/body_texture.png" in pkg_asset.resolved_mappings.values(), "Deveria ancorar sob Assets/"
    assert "Assets/CustomCar/interior.unity3d" in pkg_asset.resolved_mappings.values()
    print("  -> OK: Subpasta de assets sem prefixo roteada dinamicamente para Assets/CustomCar/.")

    # -------------------------------------------------------------
    # TESTE B: Textura solta na raiz (sem pasta) associada a mod com Assets/
    # -------------------------------------------------------------
    print("\n[TESTE B] Textura solta na raiz vinculada a mod existente...")
    z_loose = make_zip("CustomCar_AddonTexture.zip", {
        "special_paint.png": b"PAINT_DATA"
    })
    pkg_loose = installer.ModPackage(z_loose)
    analyzer.analyze_package(pkg_loose)
    pkg_loose.base_group_name = "customcar"
    path_resolver.resolve_package_paths(pkg_loose)
    
    assert pkg_loose.resolved_mappings["special_paint.png"] == "Assets/CustomCar/special_paint.png"
    print("  -> OK: Textura solta roteada diretamente para Assets/CustomCar/special_paint.png.")

    # -------------------------------------------------------------
    # TESTE C: Colisão entre mods distintos com conteúdo divergente
    # Mod A instalou RaycastCore.dll (v1). Mod B traz RaycastCore.dll (v2 incompatível).
    # O instalador deve isolar: preservar v1, não travar e instalar Mod B.dll.
    # -------------------------------------------------------------
    print("\n[TESTE C] Colisão entre mods distintos com conteúdo divergente...")
    z_mod_a = make_zip("ModAlpha-1.0.zip", {
        "ModAlpha.dll": b"MOD_ALPHA_CODE",
        "RaycastCore.dll": b"RAYCAST_V1_ORIGINAL"
    })
    pkg_a = installer.ModPackage(z_mod_a)
    pkg_a.archive_sha256 = installer.calculate_file_sha256(z_mod_a)
    analyzer.analyze_package(pkg_a)
    path_resolver.resolve_package_paths(pkg_a)
    ok_a = auto_inst.install_package(pkg_a)
    assert ok_a, "Mod Alpha deveria instalar com sucesso"
    assert auto_inst.last_conflicts_count == 0

    # Agora Mod Beta tenta instalar outro RaycastCore.dll com bytes diferentes
    z_mod_b = make_zip("ModBeta-1.0.zip", {
        "ModBeta.dll": b"MOD_BETA_CODE",
        "RaycastCore.dll": b"RAYCAST_V2_DIFFERENT_INCOMPATIBLE"
    })
    pkg_b = installer.ModPackage(z_mod_b)
    pkg_b.archive_sha256 = installer.calculate_file_sha256(z_mod_b)
    analyzer.analyze_package(pkg_b)
    path_resolver.resolve_package_paths(pkg_b)
    ok_b = auto_inst.install_package(pkg_b)
    assert ok_b, "Mod Beta deveria instalar (com o conflito isolado)"
    assert auto_inst.last_conflicts_count == 1, "Deveria registrar 1 conflito isolado"
    
    # Verificar se RaycastCore.dll de Mod Alpha foi PRESERVADO
    with open(os.path.join(test_mods, "RaycastCore.dll"), "rb") as f:
        core_data = f.read()
    assert core_data == b"RAYCAST_V1_ORIGINAL", "RaycastCore.dll original não deveria ser corrompido!"
    
    # Verificar se ModBeta.dll foi instalado com sucesso
    assert os.path.isfile(os.path.join(test_mods, "ModBeta.dll")), "ModBeta.dll deveria ter sido instalado!"
    print("  -> OK: Conflito isolado com sucesso! Arquivo existente preservado e novo mod instalado.")

    # -------------------------------------------------------------
    # TESTE D: Dependência compartilhada com conteúdo idêntico
    # Mod Gamma traz RaycastCore.dll idêntico ao de Mod Alpha
    # -------------------------------------------------------------
    print("\n[TESTE D] Dependência compartilhada com conteúdo idêntico...")
    z_mod_c = make_zip("ModGamma-1.0.zip", {
        "ModGamma.dll": b"MOD_GAMMA_CODE",
        "RaycastCore.dll": b"RAYCAST_V1_ORIGINAL"  # Idêntico!
    })
    pkg_c = installer.ModPackage(z_mod_c)
    pkg_c.archive_sha256 = installer.calculate_file_sha256(z_mod_c)
    analyzer.analyze_package(pkg_c)
    path_resolver.resolve_package_paths(pkg_c)
    ok_c = auto_inst.install_package(pkg_c)
    assert ok_c
    assert auto_inst.last_conflicts_count == 0, "Conteúdo idêntico NÃO deve gerar conflito!"
    assert os.path.isfile(os.path.join(test_mods, "ModGamma.dll"))
    print("  -> OK: Arquivo idêntico compartilhado reconhecido com 0 conflitos.")

    # -------------------------------------------------------------
    # TESTE E: Múltiplos READMEs e prevenção de sobrescrita
    # -------------------------------------------------------------
    print("\n[TESTE E] Numeração e proteção de READMEs...")
    pkg_r = installer.ModPackage("TestReadme.zip")
    pkg_r.members = [
        installer.ArchiveMember("README.txt", 10, False),
        installer.ArchiveMember("readme.md", 20, False),
        installer.ArchiveMember("instructions.txt", 30, False)
    ]
    pkg_r.mod_name_detected = "ReadmeSuite"
    path_resolver.resolve_package_paths(pkg_r)
    mapped_readmes = list(pkg_r.resolved_mappings.values())
    assert "readme(ReadmeSuite).md" in mapped_readmes
    assert "readme(ReadmeSuite_2).md" in mapped_readmes
    assert "readme(ReadmeSuite_3).md" in mapped_readmes
    print("  -> OK: 3 READMEs mapeados para nomes distintos.")

    shutil.rmtree(test_dir, ignore_errors=True)
    print("\n" + "=" * 70)
    print("   TODOS OS TESTES DA AUDITORIA FORAM APROVADOS COM 100% DE SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    run_audit_tests()
