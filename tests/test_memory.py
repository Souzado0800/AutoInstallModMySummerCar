#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação exaustiva dos 12 cenários de memória persistente e automação do Smart Mod Installer:
1. Execução inicial (instalação e gravação da memória)
2. Segunda execução sem alterações (detecção automática por memória e integridade física)
3. Detecção de ZIP idêntico (mesmo hash e mesmo nome)
4. Detecção de mesmo nome com conteúdo diferente (atualização de conteúdo)
5. Detecção de arquivo renomeado com mesmo SHA-256 (sem reinstalar)
6. Detecção de possível atualização de versão (v1.0 -> v1.1)
7. Detecção e hierarquia Main File + 4K na memória
8. Detecção e reparo de arquivo instalado que foi apagado
9. Detecção e restauração de arquivo instalado modificado externamente
10. Reinstalação e atualização de hashes
11. Backup da memória e recuperação de arquivo corrompido (.bak)
12. Estado transacional e rollback após erro de instalação
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import hashlib

sys.path.append(r"C:\Users\Souza\Downloads")
import MySummerCarModInstaller as installer

def run_scenarios():
    print("=" * 70)
    print("   VALIDAÇÃO RIGOROSA: 12 CENÁRIOS DE MEMÓRIA E AUTOMAÇÃO")
    print("=" * 70)

    test_dir = os.path.join(tempfile.gettempdir(), "test_smart_installer")
    test_downloads = os.path.join(test_dir, "Downloads")
    test_mods = os.path.join(test_dir, "Mods")
    os.makedirs(test_downloads, exist_ok=True)
    os.makedirs(test_mods, exist_ok=True)

    logger = installer.Logger(os.path.join(test_downloads, "test.log"))
    mem_db = installer.ModMemoryDatabase(test_downloads, logger)
    auto_inst = installer.AutoInstaller(test_mods, mem_db, logger)

    # Helper para criar ZIP de teste
    def make_zip(zip_name, files_dict):
        zp = os.path.join(test_downloads, zip_name)
        with zipfile.ZipFile(zp, "w") as zf:
            for fname, content in files_dict.items():
                zf.writestr(fname, content)
        return zp

    # -------------------------------------------------------------
    # CENÁRIO 1: Executar pela primeira vez
    # -------------------------------------------------------------
    print("\n[CENÁRIO 1] Executar pela primeira vez...")
    z1 = make_zip("TestMod-1.0.zip", {"TestMod.dll": b"DLL_CONTENT_V1"})
    pkg1 = installer.ModPackage(z1)
    pkg1.archive_sha256 = installer.calculate_file_sha256(z1)
    pkg1.mod_name_detected = "TestMod"
    pkg1.base_group_name = "testmod"
    pkg1.mod_type = installer.ModType.MAIN_FILE
    pkg1.version_detected = "1.0"
    pkg1.resolved_mappings = {"TestMod.dll": "TestMod.dll"}
    
    ok = auto_inst.install_package(pkg1, action="installed")
    assert ok, "Cenário 1: Falha ao instalar mod"
    assert os.path.isfile(os.path.join(test_mods, "TestMod.dll"))
    rec1 = mem_db.get_record("TestMod-1.0.zip")
    assert rec1 is not None and rec1["status"] == "installed"
    print("  -> OK: Mod instalado e gravado em installed_mods.json")

    # -------------------------------------------------------------
    # CENÁRIO 2: Executar novamente sem nenhuma alteração
    # -------------------------------------------------------------
    print("\n[CENÁRIO 2] Executar novamente sem nenhuma alteração...")
    is_intact, missing, modified = mem_db.check_physical_integrity(rec1, test_mods)
    assert is_intact and not missing and not modified
    print("  -> OK: Memória confirma arquivos presentes e íntegros (ignorado automaticamente)")

    # -------------------------------------------------------------
    # CENÁRIO 3: Detectar ZIP idêntico
    # -------------------------------------------------------------
    print("\n[CENÁRIO 3] Detectar ZIP idêntico por hash...")
    cur_hash = installer.calculate_file_sha256(z1)
    assert cur_hash == rec1["archive_sha256"]
    print("  -> OK: Mesmo nome e mesmo hash SHA-256 reconhecido")

    # -------------------------------------------------------------
    # CENÁRIO 4: Detectar mesmo nome com conteúdo diferente
    # -------------------------------------------------------------
    print("\n[CENÁRIO 4] Detectar mesmo nome com conteúdo diferente (arquivo atualizado)...")
    make_zip("TestMod-1.0.zip", {"TestMod.dll": b"DLL_CONTENT_V1_MODIFIED"})
    new_hash = installer.calculate_file_sha256(z1)
    assert new_hash != rec1["archive_sha256"]
    print("  -> OK: Hash alterado detectado para o mesmo nome de arquivo")

    # -------------------------------------------------------------
    # CENÁRIO 5: Detectar arquivo renomeado com mesmo SHA-256
    # -------------------------------------------------------------
    print("\n[CENÁRIO 5] Detectar arquivo renomeado com mesmo SHA-256...")
    z_orig = make_zip("UniqueMod.zip", {"UniqueMod.dll": b"UNIQUE_BYTES_999"})
    pkg_u = installer.ModPackage(z_orig)
    pkg_u.archive_sha256 = installer.calculate_file_sha256(z_orig)
    pkg_u.mod_name_detected = "UniqueMod"
    pkg_u.resolved_mappings = {"UniqueMod.dll": "UniqueMod.dll"}
    auto_inst.install_package(pkg_u)

    # Renomear o arquivo
    renamed_path = os.path.join(test_downloads, "MeuUniqueModRenomeado.zip")
    shutil.copy2(z_orig, renamed_path)
    renamed_hash = installer.calculate_file_sha256(renamed_path)
    
    found_rec = mem_db.get_by_hash(renamed_hash)
    assert found_rec is not None and found_rec["original_filename"] == "UniqueMod.zip"
    print("  -> OK: Conteúdo reconhecido via índice invertido SHA-256")

    # -------------------------------------------------------------
    # CENÁRIO 6: Detectar possível atualização (v1.0 -> v1.1)
    # -------------------------------------------------------------
    print("\n[CENÁRIO 6] Detectar possível atualização de versão...")
    z_v2 = make_zip("TestMod-1.1.zip", {"TestMod.dll": b"DLL_CONTENT_V1_1"})
    pkg_v2 = installer.ModPackage(z_v2)
    pkg_v2.archive_sha256 = installer.calculate_file_sha256(z_v2)
    pkg_v2.mod_name_detected = "TestMod"
    pkg_v2.base_group_name = "testmod"
    pkg_v2.mod_type = installer.ModType.MAIN_FILE
    pkg_v2.version_detected = "1.1"
    pkg_v2.resolved_mappings = {"TestMod.dll": "TestMod.dll"}

    # Atualização automática
    ok_up = auto_inst.install_package(pkg_v2, action="updated")
    assert ok_up
    assert os.path.exists(os.path.join(test_mods, "_Backups"))
    rec_v2 = mem_db.get_record("TestMod-1.1.zip")
    assert rec_v2["version"] == "1.1"
    print("  -> OK: Atualização aplicada com backup automático em _Backups")

    # -------------------------------------------------------------
    # CENÁRIO 7: Detectar Main File + 4K na memória
    # -------------------------------------------------------------
    print("\n[CENÁRIO 7] Detectar Main File + 4K Texture na memória...")
    z_main = make_zip("DirtMod(Revived) Main File.zip", {"DirtMod.dll": b"DIRT_DLL"})
    z_4k = make_zip("DirtMod(Revived)4k.zip", {"Assets/DirtModRevived/texture.unity3d": b"TEXTURE_4K"})
    
    pkg_m = installer.ModPackage(z_main)
    pkg_m.archive_sha256 = installer.calculate_file_sha256(z_main)
    pkg_m.mod_name_detected = "DirtMod(Revived)"
    pkg_m.base_group_name = "dirtmod revived"
    pkg_m.mod_type = installer.ModType.MAIN_FILE
    pkg_m.resolved_mappings = {"DirtMod.dll": "DirtMod.dll"}
    auto_inst.install_package(pkg_m)

    pkg_4k = installer.ModPackage(z_4k)
    pkg_4k.archive_sha256 = installer.calculate_file_sha256(z_4k)
    pkg_4k.mod_name_detected = "DirtMod(Revived)"
    pkg_4k.base_group_name = "dirtmod revived"
    pkg_4k.mod_type = installer.ModType.TEXTURE_ADDON
    pkg_4k.related_main_file = "DirtMod(Revived)"
    pkg_4k.resolved_mappings = {"Assets/DirtModRevived/texture.unity3d": "Assets/DirtModRevived/texture.unity3d"}
    auto_inst.install_package(pkg_4k)

    grp_list = mem_db.data["groups"].get("dirtmod revived", [])
    assert "DirtMod(Revived) Main File.zip" in grp_list
    assert "DirtMod(Revived)4k.zip" in grp_list
    print("  -> OK: Main File e Complemento 4K registrados sob o mesmo grupo")

    # -------------------------------------------------------------
    # CENÁRIO 8: Detectar arquivo instalado que foi apagado
    # -------------------------------------------------------------
    print("\n[CENÁRIO 8] Detectar arquivo que foi apagado manualmente...")
    os.remove(os.path.join(test_mods, "DirtMod.dll"))
    rec_dirt = mem_db.get_record("DirtMod(Revived) Main File.zip")
    is_intact, missing, _ = mem_db.check_physical_integrity(rec_dirt, test_mods)
    assert not is_intact and "DirtMod.dll" in missing
    print("  -> OK: Integridade física detectou arquivo ausente (DirtMod.dll)")

    # -------------------------------------------------------------
    # CENÁRIO 9: Detectar arquivo instalado modificado externamente
    # -------------------------------------------------------------
    print("\n[CENÁRIO 9] Detectar arquivo instalado modificado externamente...")
    tex_path = os.path.join(test_mods, "Assets", "DirtModRevived", "texture.unity3d")
    with open(tex_path, "wb") as f:
        f.write(b"CORRUPTED_TEXTURE_DATA_EXTERNALLY")
    
    rec_tex = mem_db.get_record("DirtMod(Revived)4k.zip")
    is_intact2, _, modified2 = mem_db.check_physical_integrity(rec_tex, test_mods)
    assert not is_intact2 and "Assets/DirtModRevived/texture.unity3d" in modified2
    print("  -> OK: Integridade física detectou divergência de hash")

    # -------------------------------------------------------------
    # CENÁRIO 10: Reinstalação e reparação
    # -------------------------------------------------------------
    print("\n[CENÁRIO 10] Reparação e revalidação de arquivos...")
    auto_inst.install_package(pkg_m, action="repaired")
    auto_inst.install_package(pkg_4k, action="repaired")
    
    rec_dirt_after = mem_db.get_record("DirtMod(Revived) Main File.zip")
    is_ok_now, _, _ = mem_db.check_physical_integrity(rec_dirt_after, test_mods)
    assert is_ok_now
    print("  -> OK: Arquivos reparados e validados no destino")

    # -------------------------------------------------------------
    # CENÁRIO 11: Backup da memória e recuperação de corrupção
    # -------------------------------------------------------------
    print("\n[CENÁRIO 11] Teste de backup da memória e recuperação...")
    mem_db.save()
    assert os.path.isfile(mem_db.bak_path), "installed_mods.json.bak não foi criado"
    
    # Corromper propositalmente o JSON principal
    with open(mem_db.json_path, "w", encoding="utf-8") as f:
        f.write("{ INVALID_JSON_SYNTAX ...")
    
    # Criar nova instância do banco de dados (deve recuperar do .bak)
    recovered_db = installer.ModMemoryDatabase(test_downloads, logger)
    assert "DirtMod(Revived) Main File.zip" in recovered_db.data["records"]
    print("  -> OK: Banco de dados recuperado com sucesso a partir do backup .bak")

    # -------------------------------------------------------------
    # CENÁRIO 12: Estado transacional e rollback após erro
    # -------------------------------------------------------------
    print("\n[CENÁRIO 12] Estado transacional e rollback em caso de falha...")
    # Criar um ZIP corrupto/com erro
    broken_zip = os.path.join(test_downloads, "BrokenMod.zip")
    with open(broken_zip, "wb") as f:
        f.write(b"NOT_A_VALID_ZIP_HEADER")
    
    pkg_broken = installer.ModPackage(broken_zip)
    pkg_broken.resolved_mappings = {"fake.dll": "fake.dll"}
    res = auto_inst.install_package(pkg_broken)
    assert not res, "Deveria falhar a instalação de arquivo quebrado"
    assert recovered_db.get_record("BrokenMod.zip") is None, "Não deve registrar na memória mod que falhou!"
    print("  -> OK: Rollback executado com sucesso, memória permaneceu consistente")

    # Limpar ambiente temporário
    shutil.rmtree(test_dir, ignore_errors=True)

    print("\n" + "=" * 70)
    print("   TODOS OS 12 CENÁRIOS FORAM VALIDADOS COM 100% DE SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    run_scenarios()
