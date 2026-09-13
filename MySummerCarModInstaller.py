#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
           MY SUMMER CAR - SMART AUTO MOD INSTALLER (100% AUTOMÁTICO)
================================================================================
Localização do Script : C:\\Users\\Souza\\Downloads\\MySummerCarModInstaller.py
Pasta de Downloads     : C:\\Users\\Souza\\Downloads
Pasta de Destino       : C:\\Program Files (x86)\\Steam\\steamapps\\common\\My Summer Car\\Mods
Pasta de Backups       : C:\\Program Files (x86)\\Steam\\steamapps\\common\\My Summer Car\\Mods\\_Backups
Banco de Memória       : C:\\Users\\Souza\\Downloads\\MySummerCarModInstaller\\installed_mods.json
Log de Execução        : C:\\Users\\Souza\\Downloads\\ModInstaller.log

Autor: Antigravity (Google DeepMind)
Modo: 100% Autônomo e Automático (Sem Menus, Sem Perguntas Redundantes)
================================================================================
"""

import os
import sys
import re
import json
import time
import shutil
import hashlib
import zipfile
import subprocess
import difflib
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any, Set

# Configuração de encoding e suporte ANSI para Windows
if sys.platform == "win32":
    try:
        os.system("")  # Ativa suporte a sequências ANSI no Windows 10/11
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Suporte opcional à biblioteca rarfile
try:
    import rarfile
    HAS_RARFILE_LIB = True
except ImportError:
    rarfile = None
    HAS_RARFILE_LIB = False


def get_default_downloads_dir() -> str:
    home_dl = os.path.join(os.path.expanduser("~"), "Downloads")
    if os.path.isdir(home_dl):
        return home_dl
    specific = r"C:\Users\Souza\Downloads"
    if os.path.isdir(specific):
        return specific
    parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if os.path.basename(parent).lower() == "downloads":
        return parent
    return os.getcwd()

def get_default_mods_dir() -> str:
    steam_default = r"C:\Program Files (x86)\Steam\steamapps\common\My Summer Car\Mods"
    if os.path.isdir(steam_default):
        return steam_default
    for d in ("C", "D", "E", "F", "G"):
        candidate = f"{d}:\\SteamLibrary\\steamapps\\common\\My Summer Car\\Mods"
        if os.path.isdir(candidate):
            return candidate
        candidate2 = f"{d}:\\Program Files (x86)\\Steam\\steamapps\\common\\My Summer Car\\Mods"
        if os.path.isdir(candidate2):
            return candidate2
    return steam_default

DEFAULT_DOWNLOADS_DIR = get_default_downloads_dir()
DEFAULT_MODS_DIR = get_default_mods_dir()
BACKUP_DIR_NAME = "_Backups"
MEMORY_FOLDER_NAME = "MySummerCarModInstaller"
MEMORY_FILE_NAME = "installed_mods.json"
LOG_FILE_NAME = "ModInstaller.log"

DANGEROUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".ps1", ".vbs", ".scr", ".msi", ".com", ".pif", ".reg"}
MOD_CODE_EXTENSIONS = {".dll"}
ASSET_EXTENSIONS = {".unity3d", ".assets", ".bundle", ".sharedassets", ".resS"}
TEXTURE_EXTENSIONS = {".png", ".dds", ".jpg", ".jpeg", ".tga", ".bmp", ".tex"}
CONFIG_EXTENSIONS = {".xml", ".ini", ".cfg", ".json", ".yaml", ".yml"}
TRANSLATION_EXTENSIONS = {".txt", ".json", ".csv"}
DOC_EXTENSIONS = {".txt", ".md", ".pdf", ".rtf", ".html"}


# ==============================================================================
# SISTEMA DE CORES E FORMATAÇÃO DE TERMINAL
# ==============================================================================
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

COLOR_ENABLED = sys.stdout.isatty() or True

def c_text(text: str, color: str) -> str:
    if not COLOR_ENABLED:
        return text
    return f"{color}{text}{Colors.RESET}"


# ==============================================================================
# LOGGER DETALHADO (ARQUIVO + TERMINAL)
# ==============================================================================
class Logger:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        try:
            folder = os.path.dirname(self.log_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
        except Exception:
            pass

    def log(self, message: str, level: str = "INFO", print_console: bool = False, color: str = ""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level:<7}] {message}\n"
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception:
            pass

        if print_console:
            prefix = ""
            if level == "ERROR":
                prefix = c_text("[ERRO] ", Colors.RED + Colors.BOLD)
            elif level == "WARN":
                prefix = c_text("[AVISO] ", Colors.YELLOW + Colors.BOLD)
            elif level == "SUCCESS":
                prefix = c_text("[OK] ", Colors.GREEN + Colors.BOLD)
            
            colored_msg = c_text(message, color) if color else message
            print(f"{prefix}{colored_msg}")

    def info(self, msg: str, print_console: bool = False, color: str = ""):
        self.log(msg, level="INFO", print_console=print_console, color=color)

    def success(self, msg: str, print_console: bool = False):
        self.log(msg, level="SUCCESS", print_console=print_console, color=Colors.GREEN)

    def warn(self, msg: str, print_console: bool = True):
        self.log(msg, level="WARN", print_console=print_console, color=Colors.YELLOW)

    def error(self, msg: str, print_console: bool = True):
        self.log(msg, level="ERROR", print_console=print_console, color=Colors.RED)

    def section(self, title: str):
        bar = "=" * 60
        self.log(f"\n{bar}\n {title.center(58)}\n{bar}", level="SECTION", print_console=False)


# ==============================================================================
# LEITORES DE ARQUIVOS COMPACTADOS (ZIP & RAR COM UNRAR EMBUTIDO)
# ==============================================================================
class ArchiveMember:
    def __init__(self, filename: str, file_size: int, is_dir: bool):
        self.filename = filename.replace("\\", "/")
        self.file_size = file_size
        self.is_dir = is_dir

    def __repr__(self):
        return f"<Member: {self.filename} ({self.file_size} bytes)>"


class BaseArchiveReader:
    def get_members(self) -> List[ArchiveMember]:
        raise NotImplementedError
    def read_bytes(self, member_name: str) -> bytes:
        raise NotImplementedError
    def close(self):
        pass


class ZipReader(BaseArchiveReader):
    def __init__(self, archive_path: str):
        self.archive_path = archive_path
        self.zip_file = zipfile.ZipFile(archive_path, 'r')

    def get_members(self) -> List[ArchiveMember]:
        members = []
        for info in self.zip_file.infolist():
            name = info.filename
            try:
                if info.flag_bits & 0x800 == 0:
                    name = name.encode('cp437').decode('utf-8', errors='replace')
            except Exception:
                pass
            is_dir = info.is_dir() or name.endswith("/")
            members.append(ArchiveMember(name, info.file_size, is_dir))
        return members

    def read_bytes(self, member_name: str) -> bytes:
        norm = member_name.replace("\\", "/")
        for info in self.zip_file.infolist():
            if info.filename.replace("\\", "/") == norm:
                return self.zip_file.read(info)
        return self.zip_file.read(member_name)

    def close(self):
        self.zip_file.close()


class RarReader(BaseArchiveReader):
    def __init__(self, archive_path: str, logger: Logger):
        self.archive_path = archive_path
        self.logger = logger
        self.unrar_tool = self._find_unrar_tool()
        self.rarfile_inst = None

        if HAS_RARFILE_LIB and self.unrar_tool:
            try:
                rarfile.UNRAR_TOOL = self.unrar_tool
                self.rarfile_inst = rarfile.RarFile(archive_path, 'r')
            except Exception:
                self.rarfile_inst = None

    def _find_unrar_tool(self) -> Optional[str]:
        candidates = [
            r"C:\Program Files\WinRAR\UnRAR.exe",
            r"C:\Program Files\WinRAR\Rar.exe",
            r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
            r"C:\Program Files\7-Zip\7z.exe",
            "unrar",
            "unrar.exe"
        ]
        for c in candidates:
            if os.path.isabs(c) and os.path.isfile(c):
                return c
            elif not os.path.isabs(c):
                found = shutil.which(c)
                if found:
                    return found
        return None

    def get_members(self) -> List[ArchiveMember]:
        if self.rarfile_inst:
            try:
                members = []
                for info in self.rarfile_inst.infolist():
                    members.append(ArchiveMember(info.filename, info.file_size, info.isdir()))
                return members
            except Exception:
                pass

        if not self.unrar_tool:
            raise RuntimeError("UnRAR.exe ou 7-Zip não encontrado para abrir arquivos .RAR.")

        tool_lower = self.unrar_tool.lower()
        if "7z" in tool_lower:
            cmd = [self.unrar_tool, "l", "-slt", self.archive_path]
            res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
            if res.returncode != 0:
                raise RuntimeError(f"7-Zip erro: {res.stderr}")
            members = []
            cur_path = None
            cur_size = 0
            cur_is_dir = False
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.startswith("Path = "):
                    cur_path = line[7:]
                elif line.startswith("Size = "):
                    try:
                        cur_size = int(line[7:])
                    except ValueError:
                        cur_size = 0
                elif line.startswith("Folder = "):
                    cur_is_dir = (line[9:] == "+")
                elif line == "" and cur_path and cur_path != self.archive_path:
                    members.append(ArchiveMember(cur_path, cur_size, cur_is_dir))
                    cur_path = None
                    cur_size = 0
                    cur_is_dir = False
            if cur_path and cur_path != self.archive_path:
                members.append(ArchiveMember(cur_path, cur_size, cur_is_dir))
            return members
        else:
            cmd = [self.unrar_tool, "vb", self.archive_path]
            res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
            if res.returncode != 0:
                raise RuntimeError(f"UnRAR erro: {res.stderr}")
            members = []
            for line in res.stdout.splitlines():
                name = line.strip()
                if not name:
                    continue
                is_dir = name.endswith("/") or name.endswith("\\")
                members.append(ArchiveMember(name, 0, is_dir))
            return members

    def read_bytes(self, member_name: str) -> bytes:
        if self.rarfile_inst:
            try:
                norm = member_name.replace("\\", "/")
                for info in self.rarfile_inst.infolist():
                    if info.filename.replace("\\", "/") == norm:
                        return self.rarfile_inst.read(info)
                return self.rarfile_inst.read(member_name)
            except Exception:
                pass

        if not self.unrar_tool:
            raise RuntimeError("Ferramenta UnRAR indisponível.")

        tool_lower = self.unrar_tool.lower()
        if "7z" in tool_lower:
            cmd = [self.unrar_tool, "e", "-so", self.archive_path, member_name]
        else:
            cmd = [self.unrar_tool, "p", "-inul", self.archive_path, member_name]

        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(f"Falha ao extrair bytes de {member_name} do RAR.")
        return res.stdout

    def close(self):
        if self.rarfile_inst:
            try:
                self.rarfile_inst.close()
            except Exception:
                pass


def open_archive(archive_path: str, logger: Logger) -> BaseArchiveReader:
    ext = os.path.splitext(archive_path)[1].lower()
    if ext == ".zip":
        return ZipReader(archive_path)
    elif ext == ".rar":
        return RarReader(archive_path, logger)
    else:
        raise ValueError(f"Formato não suportado: {ext}")


def calculate_file_sha256(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# BANCO DE MEMÓRIA LOCAL E PERSISTENTE (MOD MEMORY DATABASE)
# ==============================================================================
class ModMemoryDatabase:
    """
    Gerencia a persistência em installed_mods.json com backup em .bak.
    Opera 100% localmente e suporta transacionalidade com rollback.
    """
    def __init__(self, base_downloads_dir: str, logger: Logger):
        self.dir_path = os.path.join(base_downloads_dir, MEMORY_FOLDER_NAME)
        self.json_path = os.path.join(self.dir_path, MEMORY_FILE_NAME)
        self.bak_path = self.json_path + ".bak"
        self.logger = logger
        self.data: Dict[str, Any] = {
            "schema_version": "2.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "records": {},      # {original_filename: record_dict}
            "hash_index": {},   # {archive_sha256: original_filename}
            "groups": {},       # {mod_group_name: [filenames]}
            "history": []       # [{timestamp, action, filename, details}]
        }
        self.load()

    def _ensure_dir(self):
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path, exist_ok=True)
            except Exception:
                pass

    def load(self):
        self._ensure_dir()
        loaded = False
        if os.path.isfile(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, dict) and "records" in content:
                        self.data = content
                        loaded = True
            except Exception as e:
                self.logger.warn(f"Falha ao ler {MEMORY_FILE_NAME} ({e}). Tentando backup .bak...")

        if not loaded and os.path.isfile(self.bak_path):
            try:
                with open(self.bak_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, dict) and "records" in content:
                        self.data = content
                        self.logger.info("Memória restaurada com sucesso a partir do backup .bak!")
                        loaded = True
            except Exception as e:
                self.logger.error(f"Falha ao carregar backup da memória: {e}")

        # Reconstruir índice de hashes e file_ownership
        self.data.setdefault("hash_index", {})
        for fn, rec in self.data.get("records", {}).items():
            h = rec.get("archive_sha256")
            if h:
                self.data["hash_index"][h] = fn

        self.data.setdefault("file_ownership", {})
        if not self.data["file_ownership"]:
            for fn, rec in self.data.get("records", {}).items():
                grp = rec.get("mod_group", "")
                mname = rec.get("mod_name", "")
                hashes = rec.get("file_hashes", {})
                for rel in rec.get("installed_files", []):
                    if rel not in self.data["file_ownership"]:
                        self.data["file_ownership"][rel] = {
                            "mod_group": grp,
                            "mod_name": mname,
                            "filename": fn,
                            "sha256": hashes.get(rel, "")
                        }

    def save(self):
        self._ensure_dir()
        self.data["updated_at"] = datetime.now().isoformat()
        temp_file = self.json_path + ".tmp"
        try:
            # 1. Gravar em arquivo temporário
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            # 2. Criar backup do JSON existente
            if os.path.isfile(self.json_path):
                shutil.copy2(self.json_path, self.bak_path)
            
            # 3. Substituição atômica
            if os.path.isfile(self.json_path):
                os.replace(temp_file, self.json_path)
            else:
                os.rename(temp_file, self.json_path)
        except Exception as e:
            self.logger.error(f"Erro ao salvar memória em {self.json_path}: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def get_record(self, filename: str) -> Optional[Dict[str, Any]]:
        return self.data.get("records", {}).get(filename)

    def get_by_hash(self, archive_sha256: str) -> Optional[Dict[str, Any]]:
        fn = self.data.get("hash_index", {}).get(archive_sha256)
        if fn:
            return self.get_record(fn)
        return None

    def get_file_owner(self, rel_path: str) -> Optional[Dict[str, Any]]:
        norm_low = rel_path.replace("\\", "/").lower()
        file_ownership = self.data.get("file_ownership", {})
        for k, v in file_ownership.items():
            if k.replace("\\", "/").lower() == norm_low:
                return v
        return None

    def check_physical_integrity(self, record: Dict[str, Any], mods_dir: str) -> Tuple[bool, List[str], List[str]]:
        """
        Verifica se os arquivos instalados registrados continuam presentes e íntegros no disco.
        Retorna: (is_intact, missing_files, modified_files)
        """
        missing = []
        modified = []
        installed_files = record.get("installed_files", [])
        expected_hashes = record.get("file_hashes", {})
        expected_sizes = record.get("file_sizes", {})

        for rel_path in installed_files:
            abs_path = os.path.join(mods_dir, rel_path)
            if not os.path.isfile(abs_path):
                missing.append(rel_path)
            else:
                # Verificação rápida de tamanho primeiro
                exp_size = expected_sizes.get(rel_path)
                if exp_size is not None and os.path.getsize(abs_path) != exp_size:
                    modified.append(rel_path)
                else:
                    # Checagem de hash se houver divergência potencial
                    exp_hash = expected_hashes.get(rel_path)
                    if exp_hash:
                        cur_hash = calculate_file_sha256(abs_path)
                        if cur_hash != exp_hash:
                            modified.append(rel_path)

        is_intact = (len(missing) == 0 and len(modified) == 0)
        return is_intact, missing, modified

    def record_installation(self, pkg: "ModPackage", installed_files_info: Dict[str, Tuple[str, int]], action: str = "installed"):
        fn = pkg.filename
        existing_rec = self.get_record(fn)
        history = existing_rec.get("history", []) if existing_rec else []
        history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "archive_sha256": pkg.archive_sha256,
            "version": pkg.version_detected
        })

        record = {
            "original_filename": fn,
            "extension": os.path.splitext(fn)[1].lower(),
            "original_path": pkg.file_path,
            "file_size": pkg.file_size,
            "archive_sha256": pkg.archive_sha256,
            "analyzed_at": datetime.now().isoformat(),
            "installed_at": datetime.now().isoformat(),
            "mod_name": pkg.mod_name_detected,
            "mod_group": pkg.base_group_name,
            "mod_type": pkg.mod_type,
            "priority": pkg.priority,
            "confidence": pkg.confidence,
            "version": pkg.version_detected,
            "status": "installed",
            "related_main_file": pkg.related_main_file,
            "installed_files": list(installed_files_info.keys()),
            "file_hashes": {k: v[0] for k, v in installed_files_info.items()},
            "file_sizes": {k: v[1] for k, v in installed_files_info.items()},
            "history": history
        }

        self.data["records"][fn] = record
        if pkg.archive_sha256:
            self.data["hash_index"][pkg.archive_sha256] = fn

        # Vincular ao grupo
        group_key = pkg.base_group_name or pkg.mod_name_detected
        if group_key:
            group_list = self.data["groups"].setdefault(group_key, [])
            if fn not in group_list:
                group_list.append(fn)

        # Atualizar file_ownership
        file_ownership = self.data.setdefault("file_ownership", {})
        for rel_target, (h, sz) in installed_files_info.items():
            file_ownership[rel_target] = {
                "mod_group": group_key,
                "mod_name": pkg.mod_name_detected,
                "filename": fn,
                "sha256": h
            }

        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "filename": fn,
            "mod_name": pkg.mod_name_detected,
            "action": action
        })
        self.save()


# ==============================================================================
# MODELOS DE DADOS E CLASSIFICAÇÃO
# ==============================================================================
class ModType:
    MAIN_FILE = "MAIN FILE"
    TEXTURE_ADDON = "TEXTURE / ADDON"
    ADDON = "ADDON"
    PATCH_FIX = "PATCH / FIX"
    UPDATE = "UPDATE"
    DEPENDENCY = "DEPENDÊNCIA"
    TRANSLATION = "TRADUÇÃO"
    CONFIG = "CONFIGURAÇÃO"
    OPTIONAL = "ARQUIVO OPCIONAL"
    DOCUMENTATION = "DOCUMENTAÇÃO"
    INDEPENDENT = "ARQUIVO INDEPENDENTE"


class ModPackage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.archive_sha256 = ""
        
        self.mod_name_detected = ""
        self.base_group_name = ""
        self.version_detected = ""
        self.mod_type = ModType.INDEPENDENT
        self.priority = 50
        self.confidence = 50.0
        
        self.members: List[ArchiveMember] = []
        self.has_dll = False
        self.has_assets = False
        self.has_textures = False
        self.has_readme = False
        self.has_dangerous_files = False
        self.dangerous_files_list: List[str] = []
        self.detected_dependencies: List[str] = []
        self.readme_members: List[str] = []
        
        self.resolved_mappings: Dict[str, str] = {}
        self.related_main_file: Optional[str] = None
        self.is_group_main = False
        self.decision_status = "PENDING"  # ALREADY_INSTALLED, NEW_INSTALL, UPDATE, COMPLEMENT, SKIP, ERROR
        self.decision_message = ""

    def get_asset_folders(self) -> Set[str]:
        folders = set()
        for m in self.members:
            parts = [p.strip() for p in m.filename.replace("\\", "/").split("/") if p.strip()]
            if len(parts) >= 2 and parts[0].lower() == "assets":
                folders.add(parts[1].lower())
        return folders

    def get_mod_dlls(self) -> Set[str]:
        dlls = set()
        generic = {"mscloader.dll", "raycastcore.dll", "modapi.dll"}
        for m in self.members:
            base = os.path.basename(m.filename).lower()
            if base.endswith(".dll") and base not in generic:
                dlls.add(base)
        return dlls


class ModGroup:
    def __init__(self, group_name: str):
        self.group_name = group_name
        self.packages: List[ModPackage] = []
        self.main_package: Optional[ModPackage] = None

    def add_package(self, pkg: ModPackage):
        self.packages.append(pkg)

    def resolve_relationships(self):
        self.packages.sort(key=lambda p: p.priority, reverse=True)
        if self.packages:
            candidates = [p for p in self.packages if p.mod_type in (ModType.MAIN_FILE, ModType.DEPENDENCY, ModType.INDEPENDENT)]
            if candidates:
                self.main_package = candidates[0]
            else:
                self.main_package = self.packages[0]
            
            self.main_package.is_group_main = True
            if self.main_package.mod_name_detected:
                self.group_name = self.main_package.mod_name_detected

            for p in self.packages:
                if p != self.main_package:
                    p.related_main_file = self.main_package.mod_name_detected


# ==============================================================================
# NORMALIZAÇÃO DE NOMES E DETECÇÃO DE RELACIONAMENTO
# ==============================================================================
class ModNormalizer:
    @staticmethod
    def clean_nexus_suffix(name: str) -> str:
        cleaned = re.sub(r'[-_]\d+-[0-9a-zA-Z]+(?:-[0-9a-zA-Z]+)*-\d{9,12}$', '', name)
        cleaned = re.sub(r'\s*\d+\s+[\d\.]+\s+\d{4}-\d{2}-\d{2}T.*$', '', cleaned)
        cleaned = re.sub(r'[-_]\d{9,12}$', '', cleaned)
        return cleaned.strip()

    @staticmethod
    def extract_version(filename: str) -> str:
        # Tenta extrair versão semântica ou de upload
        match = re.search(r'\bv?(\d+(?:\.\d+)+(?:[a-zA-Z])?)\b', filename)
        if match:
            return match.group(1)
        nexus_match = re.search(r'[-_]\d+-([0-9a-zA-Z]+(?:-[0-9a-zA-Z]+)*)-\d{9,12}', filename)
        if nexus_match:
            return nexus_match.group(1).replace("-", ".")
        return ""

    @staticmethod
    def extract_mod_title(filename: str) -> str:
        base, _ = os.path.splitext(filename)
        cleaned = ModNormalizer.clean_nexus_suffix(base)
        cleaned = re.sub(r'\s+v?\d+(\.\d+)+$', '', cleaned, flags=re.IGNORECASE)
        t = re.sub(r'\b(main file|main mod|main)\b', '', cleaned, flags=re.IGNORECASE)
        t = re.sub(r'\b(4k|2k|8k|hd|ultra hd|texture|textures)\b', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\s+', ' ', t).strip(' -_')
        return t or cleaned

    @staticmethod
    def get_base_group_key(filename: str) -> str:
        base, _ = os.path.splitext(filename)
        cleaned = ModNormalizer.clean_nexus_suffix(base)
        keywords_to_strip = [
            r'\bmain file\b', r'\bmain mod\b', r'\bmain\b', r'\bcore mod\b', r'\bbase mod\b',
            r'\boriginal\b', r'\bfull\b', r'\bcomplete\b',
            r'\b4k\b', r'\b2k\b', r'\b8k\b', r'\bhd\b', r'\bultra hd\b',
            r'\btexture\b', r'\btextures\b', r'\bretexture\b', r'\bhigh res\b', r'\blow res\b',
            r'\baddon\b', r'\badd-on\b', r'\bpatch\b', r'\bfix\b', r'\bhotfix\b',
            r'\bupdate\b', r'\boptional file\b', r'\boptional\b',
            r'\bv?\d+(\.\d+)+[a-z]?\b'
        ]
        result = cleaned
        for kw in keywords_to_strip:
            result = re.sub(kw, ' ', result, flags=re.IGNORECASE)
        result = re.sub(r'[\(\)\[\]\-_]', ' ', result)
        result = re.sub(r'\s+', ' ', result).strip().lower()
        return result

    @staticmethod
    def are_mods_related(pkg_a: ModPackage, pkg_b: ModPackage) -> Tuple[bool, float]:
        if pkg_a.base_group_name and pkg_a.base_group_name == pkg_b.base_group_name:
            return True, 0.98

        dlls_a = pkg_a.get_mod_dlls()
        dlls_b = pkg_b.get_mod_dlls()
        if dlls_a and dlls_b and dlls_a.intersection(dlls_b):
            return True, 0.96

        assets_a = pkg_a.get_asset_folders()
        assets_b = pkg_b.get_asset_folders()
        if assets_a and assets_b and assets_a.intersection(assets_b):
            return True, 0.95

        for dll in dlls_a:
            dll_norm = re.sub(r'[\(\)\[\]\-_ ]', '', dll.replace('.dll', '').lower())
            for asset_f in assets_b:
                asset_norm = re.sub(r'[\(\)\[\]\-_ ]', '', asset_f.lower())
                if dll_norm == asset_norm or (len(dll_norm) > 4 and dll_norm in asset_norm):
                    return True, 0.94

        for dll in dlls_b:
            dll_norm = re.sub(r'[\(\)\[\]\-_ ]', '', dll.replace('.dll', '').lower())
            for asset_f in assets_a:
                asset_norm = re.sub(r'[\(\)\[\]\-_ ]', '', asset_f.lower())
                if dll_norm == asset_norm or (len(dll_norm) > 4 and dll_norm in asset_norm):
                    return True, 0.94

        words_a = pkg_a.base_group_name.split()
        words_b = pkg_b.base_group_name.split()
        if words_a and words_b:
            last_a = words_a[-1]
            last_b = words_b[-1]
            if (last_a.isdigit() or last_b.isdigit()) and last_a != last_b:
                return False, 0.0

        ratio = difflib.SequenceMatcher(None, pkg_a.base_group_name, pkg_b.base_group_name).ratio()
        if ratio >= 0.92:
            return True, ratio

        return False, ratio


# ==============================================================================
# MOTOR INTELIGENTE DE ANÁLISE E PONTUAÇÃO (MOD ANALYZER)
# ==============================================================================
class ModAnalyzer:
    def __init__(self, logger: Logger):
        self.logger = logger

    def analyze_package(self, pkg: ModPackage) -> bool:
        try:
            reader = open_archive(pkg.file_path, self.logger)
            pkg.members = reader.get_members()
        except Exception as e:
            self.logger.error(f"Falha ao inspecionar {pkg.filename}: {e}")
            pkg.confidence = 0.0
            return False

        pkg.mod_name_detected = ModNormalizer.extract_mod_title(pkg.filename)
        pkg.base_group_name = ModNormalizer.get_base_group_key(pkg.filename)
        pkg.version_detected = ModNormalizer.extract_version(pkg.filename)

        non_dir_members = [m for m in pkg.members if not m.is_dir]
        file_exts = {os.path.splitext(m.filename)[1].lower() for m in non_dir_members}

        pkg.has_dll = any(ext in MOD_CODE_EXTENSIONS for ext in file_exts)
        pkg.has_assets = any(ext in ASSET_EXTENSIONS for ext in file_exts)
        pkg.has_textures = any(ext in TEXTURE_EXTENSIONS for ext in file_exts)
        
        for m in non_dir_members:
            ext = os.path.splitext(m.filename)[1].lower()
            if ext in DANGEROUS_EXTENSIONS:
                pkg.has_dangerous_files = True
                pkg.dangerous_files_list.append(m.filename)

        for m in non_dir_members:
            base_name = os.path.basename(m.filename).lower()
            if base_name in ("readme.txt", "readme.md", "leiame.txt", "instructions.txt", "info.txt"):
                pkg.has_readme = True
                pkg.readme_members.append(m.filename)

        self._detect_dependencies(pkg, reader)
        reader.close()

        self._calculate_scores_and_classification(pkg)
        return True

    def _detect_dependencies(self, pkg: ModPackage, reader: BaseArchiveReader):
        text_to_scan = ""
        for m in pkg.members:
            fn_low = os.path.basename(m.filename).lower()
            if fn_low == "raycastcore.dll":
                pkg.detected_dependencies.append("RaycastCore (incluso no pacote)")

        for readme_file in pkg.readme_members[:2]:
            try:
                raw = reader.read_bytes(readme_file)
                text = raw[:16384].decode("utf-8", errors="replace")
                text_to_scan += "\n" + text
            except Exception:
                pass

        if text_to_scan:
            dep_patterns = [
                (r'(?:requires|requer|dependency|dependencia|needs)\s*[:\-]?\s*(mscloader\s*(?:pro)?)', "MSCLoader"),
                (r'(?:requires|requer|dependency|dependencia|needs)\s*[:\-]?\s*(modapi)', "ModAPI"),
                (r'(?:requires|requer|dependency|dependencia|needs)\s*[:\-]?\s*(raycastcore)', "RaycastCore"),
                (r'(?:requires|requer|dependency|dependencia|needs)\s*[:\-]?\s*(playmaker)', "HutongGames PlayMaker"),
            ]
            for pat, dep_name in dep_patterns:
                if re.search(pat, text_to_scan, flags=re.IGNORECASE):
                    if dep_name not in pkg.detected_dependencies:
                        pkg.detected_dependencies.append(dep_name)

            # Extração genérica de dependências adicionais mencionadas no README
            generic_matches = re.findall(r'(?:requires|requer|dependency|dependencia|needs)\s*[:\-]\s*([a-zA-Z0-9_\-\. ]{3,30})', text_to_scan, flags=re.IGNORECASE)
            for gm in generic_matches:
                cand = gm.strip().splitlines()[0].strip()
                cand = re.sub(r'\s+', ' ', cand)
                if cand and len(cand) >= 3 and not any(cand.lower() in d.lower() for d in pkg.detected_dependencies):
                    pkg.detected_dependencies.append(cand)

    def _calculate_scores_and_classification(self, pkg: ModPackage):
        fn_lower = pkg.filename.lower()
        scores = {
            ModType.MAIN_FILE: 0,
            ModType.TEXTURE_ADDON: 0,
            ModType.ADDON: 0,
            ModType.PATCH_FIX: 0,
            ModType.UPDATE: 0,
            ModType.DEPENDENCY: 0,
            ModType.TRANSLATION: 0,
            ModType.CONFIG: 0,
            ModType.OPTIONAL: 0,
            ModType.DOCUMENTATION: 0
        }

        if any(w in fn_lower for w in ["main file", "main mod", "main"]):
            scores[ModType.MAIN_FILE] += 55
        elif any(w in fn_lower for w in ["core", "base", "original", "full", "complete"]):
            scores[ModType.MAIN_FILE] += 35

        if any(w in fn_lower for w in ["4k", "2k", "8k", "hd", "ultra hd", "texture", "textures", "retexture", "resolution"]):
            scores[ModType.TEXTURE_ADDON] += 50
            scores[ModType.MAIN_FILE] -= 30

        if any(w in fn_lower for w in ["addon", "add-on", "expansion"]):
            scores[ModType.ADDON] += 40
            scores[ModType.MAIN_FILE] -= 15

        if any(w in fn_lower for w in ["patch", "fix", "hotfix", "bugfix", "compatibility"]):
            scores[ModType.PATCH_FIX] += 45
            scores[ModType.MAIN_FILE] -= 20

        if any(w in fn_lower for w in ["update", "upgrade"]):
            scores[ModType.UPDATE] += 35

        if any(w in fn_lower for w in ["localization", "translation", "traducao", "pt-br", "translate"]):
            scores[ModType.TRANSLATION] += 45

        if any(w in fn_lower for w in ["optional", "extra", "alt", "alternative"]):
            scores[ModType.OPTIONAL] += 35
            scores[ModType.MAIN_FILE] -= 20

        # Conteúdo interno tem peso decisivo
        if pkg.has_dll:
            scores[ModType.MAIN_FILE] += 45
            scores[ModType.ADDON] += 20
            scores[ModType.DEPENDENCY] += 15
            scores[ModType.TEXTURE_ADDON] -= 45
        else:
            if pkg.has_assets or pkg.has_textures:
                scores[ModType.TEXTURE_ADDON] += 60
                scores[ModType.MAIN_FILE] -= 60
            
            has_translate_txt = any("translate" in m.filename.lower() for m in pkg.members)
            if has_translate_txt:
                scores[ModType.TRANSLATION] += 65

        non_dirs = [m for m in pkg.members if not m.is_dir]
        all_docs = non_dirs and all(os.path.splitext(m.filename)[1].lower() in DOC_EXTENSIONS for m in non_dirs)
        if all_docs:
            scores[ModType.DOCUMENTATION] += 70
            scores[ModType.MAIN_FILE] = 0

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        priority_map = {
            ModType.DEPENDENCY: 110,
            ModType.MAIN_FILE: 100,
            ModType.UPDATE: 85,
            ModType.PATCH_FIX: 80,
            ModType.ADDON: 75,
            ModType.TEXTURE_ADDON: 70,
            ModType.TRANSLATION: 65,
            ModType.CONFIG: 60,
            ModType.OPTIONAL: 45,
            ModType.DOCUMENTATION: 30,
            ModType.INDEPENDENT: 50
        }

        if best_score <= 15:
            pkg.mod_type = ModType.INDEPENDENT
            pkg.priority = priority_map[ModType.INDEPENDENT]
            pkg.confidence = 70.0
        else:
            pkg.mod_type = best_type
            pkg.priority = priority_map.get(best_type, 50)
            pkg.confidence = min(99.0, max(75.0, 65.0 + (best_score * 0.40)))


# ==============================================================================
# RESOLUÇÃO CONSERVADORA DE CAMINHOS E ESTRUTURA (PATH RESOLVER)
# ==============================================================================
# RESOLUÇÃO CONSERVADORA DE CAMINHOS E ESTRUTURA (PATH RESOLVER)
# ==============================================================================
class PathResolver:
    def __init__(self, mods_dir: str, logger: Logger, memory_db: Optional[ModMemoryDatabase] = None):
        self.mods_dir = os.path.abspath(mods_dir)
        self.logger = logger
        self.memory_db = memory_db
        self.readme_counters: Dict[str, int] = {}

    def resolve_package_paths(self, pkg: ModPackage) -> bool:
        pkg.resolved_mappings.clear()
        file_members = [m for m in pkg.members if not m.is_dir]
        if not file_members:
            return True

        norm_paths = [m.filename.replace("\\", "/") for m in file_members]
        strip_prefix = ""
        try:
            cp = os.path.commonpath(norm_paths).replace("\\", "/")
        except Exception:
            cp = ""

        if cp:
            parts = [p for p in cp.split("/") if p]
            parts_low = [p.lower() for p in parts]
            if "mods" in parts_low:
                mods_idx = parts_low.index("mods")
                strip_prefix = "/".join(parts[:mods_idx + 1]) + "/"
            else:
                single_root = parts[0] + "/"
                sub_paths = [p[len(single_root):].lstrip("/") for p in norm_paths]
                has_sub_dll = any("/" not in p and p.lower().endswith(".dll") for p in sub_paths)
                has_sub_assets = any(p.lower().startswith("assets/") for p in sub_paths)
                if has_sub_dll or has_sub_assets:
                    strip_prefix = single_root
                else:
                    strip_prefix = ""

        for m in file_members:
            raw_path = m.filename
            if strip_prefix and raw_path.startswith(strip_prefix):
                rel_path = raw_path[len(strip_prefix):].lstrip("/")
            else:
                rel_path = raw_path

            base_name_low = os.path.basename(rel_path).lower()
            if base_name_low in ("readme.txt", "readme.md", "leiame.txt", "instructions.txt"):
                rel_path = self._format_readme_name(pkg.mod_name_detected)

            if not self._is_safe_path(rel_path):
                self.logger.error(f"Path Traversal bloqueado em {pkg.filename}: {raw_path}")
                continue

            pkg.resolved_mappings[m.filename] = rel_path

        # Roteamento inteligente e generalista de complementos/texturas sem DLL
        if not pkg.has_dll and (pkg.has_assets or pkg.has_textures):
            for orig_m, mapped in list(pkg.resolved_mappings.items()):
                mapped_norm = mapped.replace("\\", "/")
                parts = [p for p in mapped_norm.split("/") if p]
                if not parts:
                    continue
                first = parts[0].lower()
                if first not in ("assets", "config", "references") and not mapped_norm.lower().startswith("readme"):
                    disk_asset_dir = os.path.join(self.mods_dir, "Assets", parts[0])
                    if os.path.isdir(disk_asset_dir):
                        pkg.resolved_mappings[orig_m] = "Assets/" + mapped_norm
                    elif len(parts) == 1:
                        target_asset_dir = self._find_matching_asset_dir(pkg)
                        if target_asset_dir:
                            pkg.resolved_mappings[orig_m] = f"Assets/{target_asset_dir}/{mapped_norm}"
                        else:
                            clean_t = re.sub(r'[\\/:*?"<>| ]', '', pkg.mod_name_detected) or "Assets"
                            pkg.resolved_mappings[orig_m] = f"Assets/{clean_t}/{mapped_norm}"
                    else:
                        pkg.resolved_mappings[orig_m] = "Assets/" + mapped_norm

        return True

    def _find_matching_asset_dir(self, pkg: ModPackage) -> Optional[str]:
        assets_base = os.path.join(self.mods_dir, "Assets")
        if not os.path.isdir(assets_base):
            return None
        existing_dirs = [d for d in os.listdir(assets_base) if os.path.isdir(os.path.join(assets_base, d))]
        if not existing_dirs:
            return None

        candidates = [pkg.base_group_name, pkg.mod_name_detected]
        if pkg.related_main_file:
            candidates.insert(0, pkg.related_main_file)

        for cand in candidates:
            if not cand:
                continue
            cand_norm = re.sub(r'[\(\)\[\]\-_ ]', '', cand.lower())
            for ed in existing_dirs:
                ed_norm = re.sub(r'[\(\)\[\]\-_ ]', '', ed.lower())
                if cand_norm == ed_norm or (len(cand_norm) > 4 and cand_norm in ed_norm) or (len(ed_norm) > 4 and ed_norm in cand_norm):
                    return ed
        return None

    def _format_readme_name(self, mod_name: str) -> str:
        clean_name = re.sub(r'[\\/:*?"<>|]', '_', mod_name).strip() or "Mod"
        count = self.readme_counters.get(clean_name, 0) + 1
        self.readme_counters[clean_name] = count
        name = f"readme({clean_name}).md" if count == 1 else f"readme({clean_name}_{count}).md"

        # Proteção contra sobrescrita de README de outro mod existente em disco
        while True:
            dest = os.path.join(self.mods_dir, name)
            if not os.path.isfile(dest):
                break
            owner = None
            if hasattr(self, 'memory_db') and self.memory_db:
                owner = self.memory_db.get_file_owner(name)
            if owner and owner.get("mod_name", "").lower() == mod_name.lower():
                break
            count += 1
            self.readme_counters[clean_name] = count
            name = f"readme({clean_name}_{count}).md"

        return name

    def _is_safe_path(self, rel_path: str) -> bool:
        if ".." in rel_path or rel_path.startswith("/") or rel_path.startswith("\\"):
            return False
        dest_abs = os.path.abspath(os.path.join(self.mods_dir, rel_path))
        common = os.path.commonpath([self.mods_dir, dest_abs])
        return common == self.mods_dir


# ==============================================================================
# GERENCIADOR DE CONFLITOS E BACKUPS (CONFLICT MANAGER)
# ==============================================================================
class ConflictManager:
    def __init__(self, mods_dir: str, logger: Logger):
        self.mods_dir = os.path.abspath(mods_dir)
        self.backup_dir = os.path.join(self.mods_dir, BACKUP_DIR_NAME)
        self.logger = logger

    def check_destination(self, rel_target: str, new_data: bytes) -> Tuple[bool, bool, Optional[str]]:
        dest_path = os.path.join(self.mods_dir, rel_target)
        if not os.path.isfile(dest_path):
            return False, False, None
        existing_hash = calculate_file_sha256(dest_path)
        new_hash = hashlib.sha256(new_data).hexdigest()
        return True, (existing_hash == new_hash), existing_hash

    def create_backup(self, dest_path: str) -> Optional[str]:
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, exist_ok=True)
            filename = os.path.basename(dest_path)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"{filename}_{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)
            shutil.copy2(dest_path, backup_path)
            self.logger.info(f"Backup de segurança criado: {backup_name}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Falha ao criar backup de {dest_path}: {e}")
            return None


# ==============================================================================
# MOTOR AUTOMÁTICO DE INSTALAÇÃO, BACKUP E ROLLBACK (AUTO INSTALLER)
# ==============================================================================
class AutoInstaller:
    def __init__(self, mods_dir: str, memory_db: ModMemoryDatabase, logger: Logger):
        self.mods_dir = os.path.abspath(mods_dir)
        self.backup_dir = os.path.join(self.mods_dir, BACKUP_DIR_NAME)
        self.memory_db = memory_db
        self.logger = logger
        self.conflict_mgr = ConflictManager(self.mods_dir, self.logger)
        self.create_backup = self.conflict_mgr.create_backup
        self.check_destination = self.conflict_mgr.check_destination
        self.last_conflicts_count = 0

    def install_package(self, pkg: ModPackage, action: str = "installed") -> bool:
        """
        Instalação transacional com isolamento de conflitos entre mods:
        1. Cria backups de arquivos existentes que serão alterados
        2. Isola colisões com mods diferentes (preservando arquivo existente e registrando aviso)
        3. Extrai dados e grava no destino
        4. Valida se todos os arquivos foram gravados com o hash correto
        5. Salva no banco de memória com mapeamento de ownership
        6. Se falhar, reverte arquivos recém-gravados e restaura backups
        """
        self.last_conflicts_count = 0
        created_backups: Dict[str, str] = {}   # {dest_path: backup_path}
        written_files: List[str] = []
        installed_info: Dict[str, Tuple[str, int]] = {}

        try:
            reader = open_archive(pkg.file_path, self.logger)
        except Exception as e:
            self.logger.error(f"Falha ao abrir {pkg.filename}: {e}")
            return False

        try:
            for member_name, rel_target in pkg.resolved_mappings.items():
                dest_path = os.path.join(self.mods_dir, rel_target)
                data = reader.read_bytes(member_name)

                # Formatar Readme se aplicável
                if rel_target.lower().startswith("readme") and rel_target.lower().endswith(".md"):
                    try:
                        text = data.decode("utf-8", errors="replace")
                        if not text.startswith("# "):
                            data = f"# {pkg.mod_name_detected} - Informações\n\n{text}".encode("utf-8")
                    except Exception:
                        pass

                # Verificar colisão entre mods distintos
                if os.path.isfile(dest_path):
                    existing_hash = calculate_file_sha256(dest_path)
                    new_hash = hashlib.sha256(data).hexdigest()

                    owner = self.memory_db.get_file_owner(rel_target)
                    is_different_mod = False
                    if owner:
                        owner_group = owner.get("mod_group", "")
                        pkg_group = pkg.base_group_name or pkg.mod_name_detected
                        if owner_group and pkg_group and owner_group.lower() != pkg_group.lower():
                            is_different_mod = True

                    if is_different_mod:
                        if existing_hash == new_hash:
                            # Arquivo idêntico compartilhado entre mods (ex: RaycastCore.dll idêntico)
                            dest_size = len(data)
                            installed_info[rel_target] = (existing_hash, dest_size)
                            continue
                        else:
                            # Conflito entre mods distintos com conteúdo divergente!
                            # Isolação segura: não sobrescreve o arquivo de outro mod,
                            # registra no log e continua os outros arquivos
                            owner_name = owner.get("mod_name", "outro mod")
                            self.logger.warn(f"Conflito isolado em {rel_target}: já gerenciado por '{owner_name}'. Mantendo versão existente.")
                            self.last_conflicts_count += 1
                            continue
                    else:
                        # Mesmo mod ou sem dono anterior: cria backup se alterado
                        if existing_hash != new_hash:
                            bak = self.create_backup(dest_path)
                            if bak:
                                created_backups[dest_path] = bak

                parent = os.path.dirname(dest_path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)

                with open(dest_path, "wb") as f:
                    f.write(data)
                written_files.append(dest_path)

                # Coletar informações pós-gravação
                dest_size = len(data)
                dest_hash = hashlib.sha256(data).hexdigest()
                installed_info[rel_target] = (dest_hash, dest_size)

            reader.close()

            # Validação transacional
            for rel_target, (exp_hash, exp_size) in installed_info.items():
                chk_path = os.path.join(self.mods_dir, rel_target)
                if not os.path.isfile(chk_path) or os.path.getsize(chk_path) != exp_size:
                    raise RuntimeError(f"Falha de integridade física após gravação em {rel_target}")

            # Persistência na memória
            self.memory_db.record_installation(pkg, installed_info, action=action)
            self.logger.success(f"Mod {pkg.filename} instalado e validado com sucesso!")
            return True

        except Exception as e:
            self.logger.error(f"Erro transacional ao instalar {pkg.filename}: {e}. Iniciando rollback...")
            reader.close()
            # Rollback: remover arquivos escritos e restaurar backups
            for wf in written_files:
                try:
                    if os.path.exists(wf):
                        os.remove(wf)
                except Exception:
                    pass

            for orig_dest, bak_file in created_backups.items():
                try:
                    shutil.copy2(bak_file, orig_dest)
                    self.logger.info(f"Rollback: restaurado {orig_dest} a partir do backup.")
                except Exception:
                    pass
            return False


# ==============================================================================
# ORQUESTRADOR PRINCIPAL DO SMART AUTO MOD INSTALLER (100% AUTOMÁTICO)
# ==============================================================================
def run_smart_installer(downloads_dir: Optional[str] = None, mods_dir: Optional[str] = None):
    start_time = time.time()
    downloads_dir = os.path.abspath(downloads_dir) if downloads_dir else get_default_downloads_dir()
    mods_dir = os.path.abspath(mods_dir) if mods_dir else get_default_mods_dir()
    log_path = os.path.join(downloads_dir, LOG_FILE_NAME)

    logger = Logger(log_path)
    logger.section("INÍCIO DA EXECUÇÃO AUTOMÁTICA")

    print(c_text("========================================================", Colors.CYAN + Colors.BOLD))
    print(c_text("       MY SUMMER CAR SMART AUTO MOD INSTALLER", Colors.CYAN + Colors.BOLD))
    print(c_text("========================================================", Colors.CYAN + Colors.BOLD))
    print("\nAnalisando Downloads...")

    if not os.path.isdir(downloads_dir):
        print(c_text(f"Pasta de Downloads não encontrada: {downloads_dir}", Colors.RED))
        return

    if not os.path.isdir(mods_dir):
        try:
            os.makedirs(mods_dir, exist_ok=True)
        except Exception:
            print(c_text(f"Não foi possível acessar a pasta de Mods: {mods_dir}", Colors.RED))
            return

    # 1. Localizar arquivos compactados
    raw_files = [os.path.join(downloads_dir, f) for f in os.listdir(downloads_dir)
                 if os.path.splitext(f)[1].lower() in (".zip", ".rar")]
    raw_files.sort(key=lambda x: os.path.basename(x).lower())

    count = len(raw_files)
    print(c_text(f"\n{count} arquivos compactados encontrados.\n", Colors.WHITE + Colors.BOLD))
    if count == 0:
        print("Nenhum arquivo .zip ou .rar encontrado em Downloads.")
        return

    memory_db = ModMemoryDatabase(downloads_dir, logger)
    analyzer = ModAnalyzer(logger)
    path_resolver = PathResolver(mods_dir, logger, memory_db)
    installer = AutoInstaller(mods_dir, memory_db, logger)

    stats = {
        "analyzed": count,
        "installed": 0,
        "updated": 0,
        "already_installed": 0,
        "ignored": 0,
        "conflicts": 0,
        "errors": 0
    }

    # 2. Processar cada arquivo compactado
    packages: List[ModPackage] = []
    for fpath in raw_files:
        packages.append(ModPackage(fpath))

    # Agrupar pacotes para resolver Main vs Addon
    for pkg in packages:
        pkg.mod_name_detected = ModNormalizer.extract_mod_title(pkg.filename)
        pkg.base_group_name = ModNormalizer.get_base_group_key(pkg.filename)
        pkg.version_detected = ModNormalizer.extract_version(pkg.filename)

    groups: List[ModGroup] = []
    for pkg in packages:
        matched = None
        for g in groups:
            for ep in g.packages:
                is_rel, _ = ModNormalizer.are_mods_related(pkg, ep)
                if is_rel:
                    matched = g
                    break
            if matched:
                break
        if matched:
            matched.add_package(pkg)
        else:
            ng = ModGroup(pkg.mod_name_detected or pkg.base_group_name)
            ng.add_package(pkg)
            groups.append(ng)

    for g in groups:
        g.resolve_relationships()

    # 3. Execução automática por arquivo
    for idx, pkg in enumerate(packages, 1):
        fn = pkg.filename
        print(f"[{idx}/{count}] {c_text(fn, Colors.BOLD)}...")

        # Cálculo do SHA-256 do arquivo compactado
        pkg.archive_sha256 = calculate_file_sha256(pkg.file_path)

        # Consulta à memória persistente
        mem_rec = memory_db.get_record(fn)

        # CENÁRIO 1: O arquivo já está registrado pelo nome exato
        if mem_rec:
            old_hash = mem_rec.get("archive_sha256", "")
            
            # Mesmo nome e mesmo SHA-256
            if old_hash == pkg.archive_sha256:
                # Verificar se os arquivos físicos em Mods/ continuam presentes
                is_intact, missing, modified = memory_db.check_physical_integrity(mem_rec, mods_dir)
                if is_intact:
                    mod_type_str = mem_rec.get("mod_type", "MOD")
                    conf = mem_rec.get("confidence", 95.0)
                    print(f"      {mod_type_str} | {conf:.0f}% confiança")
                    print(f"      {c_text('✓ Já instalado — ignorado', Colors.GREEN)}")
                    stats["already_installed"] += 1
                    continue
                else:
                    # Falha de integridade: reparar automaticamente
                    if missing:
                        print(f"      {c_text('⚠ Arquivos ausentes detectados em Mods/: reparando...', Colors.YELLOW)}")
                    elif modified:
                        print(f"      {c_text('⚠ Arquivos modificados externamente: restaurando versão do mod...', Colors.YELLOW)}")
            else:
                # Mesmo nome mas SHA-256 diferente -> Arquivo foi atualizado no Downloads
                print(f"      {c_text('↑ ARQUIVO ATUALIZADO DETECTADO (Novo conteúdo)', Colors.MAGENTA + Colors.BOLD)}")

        # CENÁRIO 2: Arquivo renomeado mas conteúdo idêntico já instalado
        elif memory_db.get_by_hash(pkg.archive_sha256):
            orig_rec = memory_db.get_by_hash(pkg.archive_sha256)
            is_intact, _, _ = memory_db.check_physical_integrity(orig_rec, mods_dir)
            if is_intact:
                print(f"      {c_text('✓ Conteúdo idêntico já instalado (Arquivo renomeado: ' + orig_rec.get('original_filename', '') + ')', Colors.GREEN)}")
                # Registrar o alias na memória
                memory_db.data["records"][fn] = orig_rec
                memory_db.save()
                stats["already_installed"] += 1
                continue

        # Inspecionar pacote que precisa de análise / instalação
        if not analyzer.analyze_package(pkg):
            print(f"      {c_text('✗ Erro ao abrir arquivo compactado.', Colors.RED)}")
            stats["errors"] += 1
            continue

        path_resolver.resolve_package_paths(pkg)

        # Detectar se é uma atualização de versão dentro do mesmo grupo
        is_update = False
        if mem_rec and mem_rec.get("archive_sha256") != pkg.archive_sha256:
            is_update = True
        else:
            # Checar se há outra versão do mesmo mod instalada no grupo
            group_records = [r for r in memory_db.data.get("records", {}).values()
                             if r.get("mod_group") == pkg.base_group_name and r.get("mod_type") == pkg.mod_type]
            if group_records:
                is_update = True

        role_label = pkg.mod_type
        if pkg.is_group_main:
            role_label = "MAIN FILE" if "main" in role_label.lower() else role_label

        print(f"      {role_label} | {pkg.confidence:.0f}% confiança")

        # Se for arquivos perigosos
        if pkg.has_dangerous_files:
            print(f"      {c_text('⚠ Executáveis/scripts contidos por segurança (não extraídos)', Colors.YELLOW)}")
            pkg.resolved_mappings = {k: v for k, v in pkg.resolved_mappings.items() if k not in pkg.dangerous_files_list}

        if is_update:
            print(f"      {c_text('↑ Atualização detectada → Atualizando com backup automático...', Colors.CYAN)}")
            success = installer.install_package(pkg, action="updated")
            stats["conflicts"] += installer.last_conflicts_count
            if success:
                print(f"      {c_text('✓ Atualizado com sucesso!', Colors.GREEN)}")
                stats["updated"] += 1
            else:
                print(f"      {c_text('✗ Falha na atualização.', Colors.RED)}")
                stats["errors"] += 1
        else:
            if pkg.related_main_file and not pkg.is_group_main:
                print(f"      {c_text('→ Novo complemento para ' + pkg.related_main_file + ' → Instalando...', Colors.CYAN)}")
            else:
                print(f"      {c_text('→ Novo mod detectado → Instalando...', Colors.CYAN)}")

            success = installer.install_package(pkg, action="installed")
            stats["conflicts"] += installer.last_conflicts_count
            if success:
                print(f"      {c_text('✓ Instalado com sucesso!', Colors.GREEN)}")
                stats["installed"] += 1
            else:
                print(f"      {c_text('✗ Falha na instalação.', Colors.RED)}")
                stats["errors"] += 1

    elapsed = time.time() - start_time

    # 4. Relatório final conciso
    print(c_text("\n========================================================", Colors.CYAN + Colors.BOLD))
    print(c_text("                    CONCLUÍDO", Colors.CYAN + Colors.BOLD))
    print(c_text("========================================================", Colors.CYAN + Colors.BOLD))
    print(f"Mods analisados  : {stats['analyzed']}")
    print(f"Novos instalados : {c_text(str(stats['installed']), Colors.GREEN if stats['installed'] > 0 else Colors.WHITE)}")
    print(f"Atualizados      : {c_text(str(stats['updated']), Colors.MAGENTA if stats['updated'] > 0 else Colors.WHITE)}")
    print(f"Já instalados    : {c_text(str(stats['already_installed']), Colors.WHITE)}")
    print(f"Ignorados        : {stats['ignored']}")
    print(f"Conflitos        : {stats['conflicts']}")
    print(f"Erros            : {c_text(str(stats['errors']), Colors.RED if stats['errors'] > 0 else Colors.WHITE)}")
    print(f"\nTempo total      : {elapsed:.2f}s")
    print(c_text("========================================================", Colors.CYAN + Colors.BOLD))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="My Summer Car Smart Auto Mod Installer")
    parser.add_argument("--downloads", type=str, default=None, help="Caminho para a pasta de Downloads contendo os .zip e .rar")
    parser.add_argument("--mods", type=str, default=None, help="Caminho para a pasta de Mods do My Summer Car")
    args, unknown = parser.parse_known_args()

    try:
        run_smart_installer(downloads_dir=args.downloads, mods_dir=args.mods)
    except (KeyboardInterrupt, EOFError):
        print("\n\nExecução interrompida.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro fatal inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
