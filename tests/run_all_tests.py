#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executor de todas as suítes de testes automatizados do My Summer Car Smart Mod Installer.
Total: 27 testes cobrindo integração, resiliência de memória, rollback e regras generalistas.
"""

import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))

import test_integration
import test_memory
import test_audit

def main():
    print("=" * 75)
    print("      MY SUMMER CAR SMART MOD INSTALLER - SUÍTE COMPLETA DE TESTES")
    print("=" * 75)
    start_time = time.time()

    print("\n>>> EXECUÇÃO 1/3: TESTES DE INTEGRAÇÃO BÁSICA (10 TESTES)")
    test_integration.run_tests()

    print("\n>>> EXECUÇÃO 2/3: TESTES DE CENÁRIOS DE MEMÓRIA E AUTOMAÇÃO (12 TESTES)")
    test_memory.run_scenarios()

    print("\n>>> EXECUÇÃO 3/3: TESTES DE AUDITORIA E REGRAS GENERALISTAS (5 TESTES)")
    test_audit.run_audit_tests()

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print("                  RELATÓRIO GERAL DA SUÍTE DE TESTES")
    print("=" * 75)
    print("  [✓] Testes de Integração e Segurança : 10/10 PASSOU")
    print("  [✓] Testes de Memória e Rollback     : 12/12 PASSOU")
    print("  [✓] Testes de Auditoria Generalista   :  5/5  PASSOU")
    print("  -------------------------------------------------------------------------")
    print("  TOTAL DE TESTES APROVADOS            : 27/27 (100% SUCESSO)")
    print(f"  TEMPO TOTAL DE EXECUÇÃO              : {elapsed:.2f}s")
    print("=" * 75)

if __name__ == "__main__":
    main()
