#!/usr/bin/env python3
"""
Sistema de Controle da Extração Histórica ANTAQ
Permite pausar, retomar e gerenciar o processo de extração
"""

import os
import json
import time
import subprocess
import signal
from datetime import datetime

class ControladorExtracao:
    def __init__(self):
        self.arquivo_estado = "estado_extracao.json"
        self.arquivo_controle = "controle_extracao.json"
        self.arquivo_principal = "data/normas_antaq_completo.parquet"
        
    def salvar_estado(self, ano_atual, progresso, total_normas=0, status="executando"):
        """Salva o estado atual da extração"""
        estado = {
            'ano_atual': ano_atual,
            'progresso': progresso,
            'total_normas': total_normas,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'anos_processados': list(range(2002, ano_atual + 1)) if ano_atual >= 2002 else []
        }
        
        with open(self.arquivo_estado, 'w') as f:
            json.dump(estado, f, indent=2)
    
    def carregar_estado(self):
        """Carrega o estado salvo da extração"""
        if os.path.exists(self.arquivo_estado):
            try:
                with open(self.arquivo_estado, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def criar_comando_pausa(self):
        """Cria comando para pausar a extração"""
        comando = {
            'acao': 'pausar',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.arquivo_controle, 'w') as f:
            json.dump(comando, f, indent=2)
        
        print("🛑 Comando de PAUSA enviado!")
        print("⏸️  O processo irá pausar após completar o ano atual")
    
    def criar_comando_parar(self):
        """Cria comando para parar completamente a extração"""
        comando = {
            'acao': 'parar',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.arquivo_controle, 'w') as f:
            json.dump(comando, f, indent=2)
        
        print("⛔ Comando de PARADA enviado!")
        print("🔄 O processo irá parar graciosamente após salvar o progresso")
    
    def limpar_comandos(self):
        """Remove arquivos de comando"""
        if os.path.exists(self.arquivo_controle):
            os.remove(self.arquivo_controle)
        print("✅ Comandos de controle limpos")
    
    def verificar_processo_ativo(self):
        """Verifica se há processo de extração executando"""
        try:
            result = subprocess.run(['pgrep', '-f', 'executar_completo_historico'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def matar_processo(self):
        """Força parada do processo (uso com cuidado)"""
        try:
            result = subprocess.run(['pgrep', '-f', 'executar_completo_historico'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"🔪 Processo {pid} terminado")
                time.sleep(2)
                return True
        except Exception as e:
            print(f"❌ Erro ao matar processo: {e}")
        return False
    
    def status(self):
        """Mostra o status atual da extração"""
        print("📊 STATUS DA EXTRAÇÃO HISTÓRICA")
        print("=" * 50)
        
        # Verifica processo
        processo_ativo = self.verificar_processo_ativo()
        status_icon = "🔄" if processo_ativo else "⏸️"
        status_text = "EXECUTANDO" if processo_ativo else "PARADO"
        print(f"{status_icon} Status do processo: {status_text}")
        
        # Estado salvo
        estado = self.carregar_estado()
        if estado:
            print(f"📅 Último ano processado: {estado.get('ano_atual', 'N/A')}")
            print(f"📈 Progresso: {estado.get('progresso', 0)}%")
            print(f"📊 Total de normas: {estado.get('total_normas', 0)}")
            print(f"🕐 Última atualização: {estado.get('timestamp', 'N/A')}")
            
            anos_proc = estado.get('anos_processados', [])
            if anos_proc:
                print(f"✅ Anos processados: {len(anos_proc)} ({min(anos_proc)}-{max(anos_proc)})")
        else:
            print("📋 Nenhum estado salvo encontrado")
        
        # Arquivo principal
        if os.path.exists(self.arquivo_principal):
            tamanho = os.path.getsize(self.arquivo_principal) / (1024*1024)
            print(f"💾 Arquivo principal: {tamanho:.1f}MB")
        else:
            print("💾 Arquivo principal: Não existe")
        
        # Comandos pendentes
        if os.path.exists(self.arquivo_controle):
            try:
                with open(self.arquivo_controle, 'r') as f:
                    cmd = json.load(f)
                print(f"⚠️  Comando pendente: {cmd.get('acao', 'unknown')}")
            except:
                pass
        
        print("")
    
    def retomar(self, ano_inicio=None, ano_fim=2024):
        """Retoma a extração de onde parou"""
        if self.verificar_processo_ativo():
            print("❌ Já existe um processo executando!")
            print("💡 Use 'python3 controlador_extracao.py status' para verificar")
            return
        
        self.limpar_comandos()
        
        # Determina de onde retomar
        if ano_inicio is None:
            estado = self.carregar_estado()
            if estado and estado.get('ano_atual'):
                # Retoma do próximo ano após o último processado
                ano_inicio = estado['ano_atual'] + 1
                print(f"🔄 Retomando da extração do ano {ano_inicio}")
            else:
                ano_inicio = 2002
                print(f"🆕 Iniciando extração do zero (ano {ano_inicio})")
        else:
            print(f"🎯 Retomando da extração do ano {ano_inicio}")
        
        if ano_inicio > ano_fim:
            print(f"✅ Extração já foi completada até {ano_fim}!")
            return
        
        # Cria script de retomada
        script_retomada = f"""#!/usr/bin/env python3
import sys
sys.path.append('.')
from executar_completo_historico import main as main_historico
from executar_completo_historico import SophiaANTAQScraper
import os
import time

# Modifica os anos para retomar de onde parou
anos_restantes = list(range({ano_inicio}, {ano_fim + 1}))
print(f"🔄 RETOMANDO EXTRAÇÃO HISTÓRICA")
print(f"📅 Anos restantes: {{len(anos_restantes)}} ({{anos_restantes[0]}}-{{anos_restantes[-1]}})")
print(f"⏱️  Estimativa: {{len(anos_restantes) * 0.5:.1f}} horas")

# Executa a extração
if __name__ == "__main__":
    from Scrap import SophiaANTAQScraper
    import pandas as pd
    from datetime import datetime
    
    scraper = SophiaANTAQScraper(
        delay=1.5,
        verify_ssl=False,
        extract_pdf_content=True
    )
    
    arquivo_principal = "data/normas_antaq_completo.parquet"
    
    # Carrega IDs existentes
    if os.path.exists(arquivo_principal):
        existing_ids_global = scraper.load_existing_ids(arquivo_principal)
        print(f"🔑 {{len(existing_ids_global)}} IDs já existentes no banco")
    else:
        existing_ids_global = set()
    
    try:
        for i, ano in enumerate(anos_restantes, 1):
            # Verifica comando de controle
            if os.path.exists('controle_extracao.json'):
                import json
                try:
                    with open('controle_extracao.json', 'r') as f:
                        cmd = json.load(f)
                    if cmd.get('acao') in ['pausar', 'parar']:
                        print(f"\\n🛑 Comando '{{cmd['acao']}}' recebido - parando graciosamente")
                        break
                except:
                    pass
            
            print(f"\\n📅 PROCESSANDO ANO {{ano}} ({{i}}/{{len(anos_restantes)}})")
            
            # Salva estado atual
            with open('estado_extracao.json', 'w') as f:
                import json
                json.dump({{
                    'ano_atual': ano,
                    'progresso': (i-1)/len(anos_restantes)*100,
                    'total_normas': len(existing_ids_global),
                    'status': 'executando',
                    'timestamp': datetime.now().isoformat()
                }}, f, indent=2)
            
            try:
                scraper.get_initial_guid()
                dados_ano = scraper.scrape_all_pages(max_pages=None, ano=ano)
                
                if dados_ano:
                    dados_novos = scraper.filter_duplicates(dados_ano, existing_ids_global)
                    if dados_novos:
                        scraper.save_to_parquet(dados_novos, arquivo_principal, merge_with_existing=True)
                        for item in dados_novos:
                            if item.get('codigo_registro'):
                                existing_ids_global.add(str(item['codigo_registro']))
                        print(f"💾 {{len(dados_novos)}} normas salvas para {{ano}}")
                    else:
                        print(f"📋 Todas as normas de {{ano}} já existiam")
                else:
                    print(f"📭 Nenhuma norma encontrada para {{ano}}")
                
                time.sleep(3)  # Pausa entre anos
                
            except Exception as e:
                print(f"❌ Erro no ano {{ano}}: {{e}}")
                continue
        
        # Salva estado final
        with open('estado_extracao.json', 'w') as f:
            json.dump({{
                'ano_atual': anos_restantes[-1] if anos_restantes else {ano_fim},
                'progresso': 100,
                'total_normas': len(existing_ids_global),
                'status': 'completo',
                'timestamp': datetime.now().isoformat()
            }}, f, indent=2)
        
        print("\\n🎉 EXTRAÇÃO HISTÓRICA FINALIZADA!")
        
    except KeyboardInterrupt:
        print("\\n⚠️  Extração interrompida pelo usuário")
    except Exception as e:
        print(f"\\n❌ Erro geral: {{e}}")
"""
        
        # Salva e executa script de retomada
        with open('retomar_extracao.py', 'w') as f:
            f.write(script_retomada)
        
        print("🚀 Iniciando extração em background...")
        subprocess.Popen(['python3', 'retomar_extracao.py'], 
                        stdout=open('log_extracao.txt', 'w'),
                        stderr=subprocess.STDOUT)
        
        time.sleep(2)
        print("✅ Processo iniciado!")
        print("💡 Use 'python3 controlador_extracao.py status' para monitorar")
        print("💡 Use 'python3 controlador_extracao.py pausar' para pausar")

def main():
    controlador = ControladorExtracao()
    
    if len(os.sys.argv) < 2:
        print("🎮 CONTROLADOR DE EXTRAÇÃO HISTÓRICA ANTAQ")
        print("=" * 50)
        print("Comandos disponíveis:")
        print("  status    - Mostra status atual")
        print("  pausar    - Pausa a extração (graciosamente)")
        print("  parar     - Para a extração completamente")
        print("  retomar   - Retoma de onde parou (2002-2024)")
        print("  retomar X - Retoma do ano X (ex: 2010)")
        print("  matar     - Força parada do processo (cuidado!)")
        print("  limpar    - Remove comandos e arquivos de controle")         
        print("")
        print("Exemplos:")
        print("  python3 controlador_extracao.py status")
        print("  python3 controlador_extracao.py retomar")
        print("  python3 controlador_extracao.py retomar 2010")
        return
    
    comando = os.sys.argv[1].lower()
    
    if comando == 'status':
        controlador.status()
    
    elif comando == 'pausar':
        controlador.criar_comando_pausa()
    
    elif comando == 'parar':
        controlador.criar_comando_parar()
    
    elif comando == 'retomar':
        ano_inicio = None
        if len(os.sys.argv) > 2:
            try:
                ano_inicio = int(os.sys.argv[2])
                if not (2002 <= ano_inicio <= 2024):
                    print("❌ Ano deve estar entre 2002 e 2024")
                    return
            except ValueError:
                print("❌ Ano deve ser um número")
                return
        controlador.retomar(ano_inicio)
    
    elif comando == 'matar':
        print("⚠️  ATENÇÃO: Isso irá forçar a parada do processo!")
        confirm = input("Digite 'CONFIRMO' para continuar: ")
        if confirm == 'CONFIRMO':
            controlador.matar_processo()
        else:
            print("❌ Operação cancelada")
    
    elif comando == 'limpar':
        controlador.limpar_comandos()
        if os.path.exists('estado_extracao.json'):
            os.remove('estado_extracao.json')
        if os.path.exists('retomar_extracao.py'):
            os.remove('retomar_extracao.py')
        print("🧹 Arquivos de controle removidos")
    
    else:
        print(f"❌ Comando desconhecido: {comando}")
        print("💡 Use sem argumentos para ver a ajuda")

if __name__ == "__main__":
    main()