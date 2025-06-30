#!/usr/bin/env python3
"""
Parser Híbrido de NFe
Combina robustez técnica do parser fornecido com funcionalidades de negócio da pasta
"""

import os
import json
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from lxml import etree

# Imports locais
from models import NotaFiscal, ItemNotaFiscal, EventoCancelamento, converter_para_decimal
from validators import ValidadorFiscal
from utils import (
    UtilXML, UtilData, UtilValor, UtilArquivo, UtilTributario, UtilLog,
    NAMESPACE_NFE, extrair_chave_acesso
)

# Configurar logging
logger = logging.getLogger(__name__)

class NFEParserHibrido:
    """
    Parser híbrido robusto para XMLs de NFe
    Combina validação robusta com funcionalidades completas de negócio
    """
    
    def __init__(self, tabela_ncm_monofasico: Optional[Dict] = None):
        self.namespace = NAMESPACE_NFE
        self.validador = ValidadorFiscal()
        self.tabela_ncm_monofasico = tabela_ncm_monofasico or {}
        self.logs_processamento = []
        self.estatisticas = {
            'total_processados': 0,
            'total_validos': 0,
            'total_invalidos': 0,
            'total_cancelados': 0
        }
    
    def processar_xml_nfe(self, xml_content: Union[str, bytes], arquivo_origem: str = "") -> Optional[NotaFiscal]:
        """
        Processa um XML de NFe com validação completa
        """
        self.estatisticas['total_processados'] += 1
        
        # Validação inicial da estrutura XML
        if not UtilXML.validar_estrutura_xml(xml_content):
            self._log_erro("Estrutura XML inválida")
            self.estatisticas['total_invalidos'] += 1
            return None
        
        try:
            # Parse do XML
            if isinstance(xml_content, str):
                xml_content = xml_content.encode('utf-8')
            
            root = etree.fromstring(xml_content)
            
            # Localizar elemento NFe
            nfe_element = self._localizar_elemento_nfe(root)
            if nfe_element is None:
                self._log_erro("Elemento NFe não encontrado")
                self.estatisticas['total_invalidos'] += 1
                return None
            
            # Criar objeto NotaFiscal
            nota_fiscal = NotaFiscal()
            nota_fiscal.arquivo_origem = arquivo_origem
            nota_fiscal.data_processamento = datetime.now()
            
            # Extrair dados principais
            if not self._extrair_dados_identificacao(nfe_element, nota_fiscal):
                self.estatisticas['total_invalidos'] += 1
                return None
            
            if not self._extrair_dados_emitente(nfe_element, nota_fiscal):
                self.estatisticas['total_invalidos'] += 1
                return None
            
            self._extrair_dados_destinatario(nfe_element, nota_fiscal)
            self._extrair_dados_totais(nfe_element, nota_fiscal)
            self._extrair_informacoes_adicionais(nfe_element, nota_fiscal)
            
            # Processar itens
            if not self._processar_itens(nfe_element, nota_fiscal):
                self.estatisticas['total_invalidos'] += 1
                return None
            
            # Recalcular totais e validar consistência
            nota_fiscal.recalcular_totais()
            self._validar_consistencia_nota(nota_fiscal)
            
            # Adicionar logs de validação
            nota_fiscal.logs_processamento.extend(self.validador.obter_logs_validacao())
            
            if nota_fiscal.valida:
                self.estatisticas['total_validos'] += 1
                self._log_info(f"NFe processada com sucesso: {nota_fiscal.numero}")
            else:
                self.estatisticas['total_invalidos'] += 1
                self._log_aviso(f"NFe processada com alertas: {nota_fiscal.numero}")
            
            return nota_fiscal
            
        except Exception as e:
            self._log_erro(f"Erro no processamento da NFe: {e}")
            self.estatisticas['total_invalidos'] += 1
            return None
    
    def processar_evento_cancelamento(self, xml_content: Union[str, bytes]) -> Optional[EventoCancelamento]:
        """
        Processa um evento de cancelamento de NFe
        """
        try:
            if isinstance(xml_content, str):
                xml_content = xml_content.encode('utf-8')
            
            root = etree.fromstring(xml_content)
            
            # Verificar se é evento de cancelamento
            tipo_evento_elem = UtilXML.encontrar_elemento(root, 'tpEvento', self.namespace)
            if tipo_evento_elem is None or tipo_evento_elem.text != '110111':
                return None
            
            # Criar evento
            evento = EventoCancelamento()
            
            # Extrair chave da NFe cancelada
            chave_elem = UtilXML.encontrar_elemento(root, 'chNFe', self.namespace)
            if chave_elem is not None:
                evento.chave_nfe = chave_elem.text
            
            # Extrair data do evento
            data_elem = UtilXML.encontrar_elemento(root, 'dhEvento', self.namespace)
            if data_elem is not None:
                evento.data_evento = UtilData.parsear_data_nfe(data_elem.text)
            
            # Extrair justificativa
            justificativa_elem = UtilXML.encontrar_elemento(root, 'xJust', self.namespace)
            if justificativa_elem is not None:
                evento.justificativa = justificativa_elem.text
            
            return evento
            
        except Exception as e:
            self._log_erro(f"Erro ao processar evento de cancelamento: {e}")
            return None
    
    def processar_diretorio(self, diretorio: str, incluir_cancelamentos: bool = True) -> Dict[str, Any]:
        """
        Processa todos os XMLs de um diretório
        """
        self._log_info(f"Iniciando processamento do diretório: {diretorio}")
        
        # Listar arquivos XML
        arquivos_xml = UtilArquivo.listar_xmls_diretorio(diretorio)
        if not arquivos_xml:
            self._log_aviso("Nenhum arquivo XML encontrado")
            return {'notas': [], 'cancelamentos': [], 'estatisticas': self.estatisticas}
        
        notas_fiscais = []
        cancelamentos = {}
        
        # Primeiro passo: identificar cancelamentos
        if incluir_cancelamentos:
            self._log_info("Identificando eventos de cancelamento...")
            for arquivo in arquivos_xml:
                conteudo_xml = UtilArquivo.ler_arquivo_xml(arquivo)
                if conteudo_xml:
                    try:
                        root = etree.fromstring(conteudo_xml.encode('utf-8'))
                        if UtilArquivo.determinar_tipo_xml(root) == 'EVENTO':
                            evento = self.processar_evento_cancelamento(conteudo_xml)
                            if evento and evento.chave_nfe:
                                cancelamentos[evento.chave_nfe] = evento
                                self._log_info(f"Cancelamento encontrado: {evento.chave_nfe}")
                    except Exception:
                        continue
        
        # Segundo passo: processar notas fiscais
        self._log_info("Processando notas fiscais...")
        for arquivo in arquivos_xml:
            conteudo_xml = UtilArquivo.ler_arquivo_xml(arquivo)
            if conteudo_xml:
                try:
                    root = etree.fromstring(conteudo_xml.encode('utf-8'))
                    if UtilArquivo.determinar_tipo_xml(root) == 'NFE':
                        nota = self.processar_xml_nfe(conteudo_xml, arquivo)
                        if nota:
                            # Verificar se foi cancelada
                            if nota.chave_acesso in cancelamentos:
                                nota.marcar_como_cancelada("Evento de cancelamento encontrado")
                                self.estatisticas['total_cancelados'] += 1
                            
                            notas_fiscais.append(nota)
                except Exception as e:
                    self._log_erro(f"Erro ao processar {arquivo}: {e}")
                    continue
        
        self._log_info(f"Processamento concluído. {len(notas_fiscais)} notas processadas.")
        
        return {
            'notas': notas_fiscais,
            'cancelamentos': list(cancelamentos.values()),
            'estatisticas': self.estatisticas,
            'logs': self.logs_processamento
        }
    
    def _localizar_elemento_nfe(self, root: etree.Element) -> Optional[etree.Element]:
        """Localiza o elemento NFe na estrutura XML"""
        if root.tag.endswith('nfeProc'):
            return UtilXML.encontrar_elemento(root, 'NFe', self.namespace)
        elif root.tag.endswith('NFe'):
            return root
        return None
    
    def _extrair_dados_identificacao(self, nfe_element: etree.Element, nota_fiscal: NotaFiscal) -> bool:
        """Extrai dados de identificação da NFe"""
        inf_nfe = UtilXML.encontrar_elemento(nfe_element, 'infNFe', self.namespace)
        if inf_nfe is None:
            nota_fiscal.adicionar_erro_validacao("Elemento infNFe não encontrado")
            return False
        
        # Chave de acesso
        nota_fiscal.chave_acesso = extrair_chave_acesso(inf_nfe) or ""
        if not self.validador.validar_chave_nfe(nota_fiscal.chave_acesso):
            nota_fiscal.adicionar_erro_validacao("Chave de acesso inválida")
        
        # Dados de identificação
        ide = UtilXML.encontrar_elemento(inf_nfe, 'ide', self.namespace)
        if ide is None:
            nota_fiscal.adicionar_erro_validacao("Elemento ide não encontrado")
            return False
        
        nota_fiscal.numero = UtilXML.obter_texto_elemento(ide, 'nNF', namespace=self.namespace)
        nota_fiscal.serie = UtilXML.obter_texto_elemento(ide, 'serie', namespace=self.namespace)
        nota_fiscal.modelo = UtilXML.obter_texto_elemento(ide, 'mod', namespace=self.namespace)
        nota_fiscal.natureza_operacao = UtilXML.obter_texto_elemento(ide, 'natOp', namespace=self.namespace)
        nota_fiscal.codigo_uf = UtilXML.obter_texto_elemento(ide, 'cUF', namespace=self.namespace)
        
        # Data de emissão
        data_emissao_str = UtilXML.obter_texto_elemento(ide, 'dhEmi', namespace=self.namespace)
        nota_fiscal.data_emissao = UtilData.parsear_data_nfe(data_emissao_str)
        
        # Validações básicas
        if not nota_fiscal.numero:
            nota_fiscal.adicionar_erro_validacao("Número da nota não encontrado")
            return False
        
        return True
    
    def _extrair_dados_emitente(self, nfe_element: etree.Element, nota_fiscal: NotaFiscal) -> bool:
        """Extrai dados do emitente"""
        inf_nfe = UtilXML.encontrar_elemento(nfe_element, 'infNFe', self.namespace)
        emit = UtilXML.encontrar_elemento(inf_nfe, 'emit', self.namespace)
        
        if emit is None:
            nota_fiscal.adicionar_erro_validacao("Dados do emitente não encontrados")
            return False
        
        # CNPJ/CPF do emitente
        cnpj = UtilXML.obter_texto_elemento(emit, 'CNPJ', namespace=self.namespace)
        cpf = UtilXML.obter_texto_elemento(emit, 'CPF', namespace=self.namespace)
        
        if cnpj:
            nota_fiscal.emitente_cnpj = cnpj
            if not self.validador.validar_cnpj(cnpj):
                nota_fiscal.adicionar_erro_validacao("CNPJ do emitente inválido")
        elif cpf:
            nota_fiscal.emitente_cnpj = cpf  # Usar mesmo campo para CPF
            if not self.validador.validar_cpf(cpf):
                nota_fiscal.adicionar_erro_validacao("CPF do emitente inválido")
        else:
            nota_fiscal.adicionar_erro_validacao("CNPJ/CPF do emitente não encontrado")
            return False
        
        # Nome do emitente
        nota_fiscal.emitente_nome = UtilXML.obter_texto_elemento(emit, 'xNome', namespace=self.namespace)
        if not nota_fiscal.emitente_nome:
            nota_fiscal.adicionar_erro_validacao("Nome do emitente não encontrado")
            return False
        
        # IE do emitente
        nota_fiscal.emitente_ie = UtilXML.obter_texto_elemento(emit, 'IE', namespace=self.namespace)
        
        # Endereço do emitente
        ender_emit = UtilXML.encontrar_elemento(emit, 'enderEmit', self.namespace)
        if ender_emit is not None:
            nota_fiscal.emitente_endereco = {
                'logradouro': UtilXML.obter_texto_elemento(ender_emit, 'xLgr', namespace=self.namespace),
                'numero': UtilXML.obter_texto_elemento(ender_emit, 'nro', namespace=self.namespace),
                'bairro': UtilXML.obter_texto_elemento(ender_emit, 'xBairro', namespace=self.namespace),
                'municipio': UtilXML.obter_texto_elemento(ender_emit, 'xMun', namespace=self.namespace),
                'uf': UtilXML.obter_texto_elemento(ender_emit, 'UF', namespace=self.namespace),
                'cep': UtilXML.obter_texto_elemento(ender_emit, 'CEP', namespace=self.namespace)
            }
        
        return True
    
    def _extrair_dados_destinatario(self, nfe_element: etree.Element, nota_fiscal: NotaFiscal):
        """Extrai dados do destinatário"""
        inf_nfe = UtilXML.encontrar_elemento(nfe_element, 'infNFe', self.namespace)
        dest = UtilXML.encontrar_elemento(inf_nfe, 'dest', self.namespace)
        
        if dest is None:
            return  # Destinatário é opcional
        
        # CNPJ/CPF do destinatário
        cnpj = UtilXML.obter_texto_elemento(dest, 'CNPJ', namespace=self.namespace)
        cpf = UtilXML.obter_texto_elemento(dest, 'CPF', namespace=self.namespace)
        
        if cnpj:
            nota_fiscal.destinatario_cnpj_cpf = cnpj
            if not self.validador.validar_cnpj(cnpj):
                nota_fiscal.adicionar_erro_validacao("CNPJ do destinatário inválido")
        elif cpf:
            nota_fiscal.destinatario_cnpj_cpf = cpf
            if not self.validador.validar_cpf(cpf):
                nota_fiscal.adicionar_erro_validacao("CPF do destinatário inválido")
        
        # Nome do destinatário
        nota_fiscal.destinatario_nome = UtilXML.obter_texto_elemento(dest, 'xNome', namespace=self.namespace)
        nota_fiscal.destinatario_ie = UtilXML.obter_texto_elemento(dest, 'IE', namespace=self.namespace)
    
    def _extrair_dados_totais(self, nfe_element: etree.Element, nota_fiscal: NotaFiscal):
        """Extrai totais da NFe"""
        inf_nfe = UtilXML.encontrar_elemento(nfe_element, 'infNFe', self.namespace)
        total = UtilXML.encontrar_elemento(inf_nfe, 'total', self.namespace)
        
        if total is None:
            return
        
        icms_tot = UtilXML.encontrar_elemento(total, 'ICMSTot', self.namespace)
        if icms_tot is not None:
            nota_fiscal.valor_produtos = converter_para_decimal(
                UtilXML.obter_texto_elemento(icms_tot, 'vProd', "0", self.namespace)
            )
            nota_fiscal.valor_total_nf = converter_para_decimal(
                UtilXML.obter_texto_elemento(icms_tot, 'vNF', "0", self.namespace)
            )
            nota_fiscal.valor_desconto_total = converter_para_decimal(
                UtilXML.obter_texto_elemento(icms_tot, 'vDesc', "0", self.namespace)
            )
            nota_fiscal.valor_pis_total = converter_para_decimal(
                UtilXML.obter_texto_elemento(icms_tot, 'vPIS', "0", self.namespace)
            )
            nota_fiscal.valor_cofins_total = converter_para_decimal(
                UtilXML.obter_texto_elemento(icms_tot, 'vCOFINS', "0", self.namespace)
            )
    
    def _extrair_informacoes_adicionais(self, nfe_element: etree.Element, nota_fiscal: NotaFiscal):
        """Extrai informações adicionais"""
        inf_nfe = UtilXML.encontrar_elemento(nfe_element, 'infNFe', self.namespace)
        inf_adic = UtilXML.encontrar_elemento(inf_nfe, 'infAdic', self.namespace)
        
        if inf_adic is not None:
            nota_fiscal.informacoes_adicionais = UtilXML.obter_texto_elemento(
                inf_adic, 'infCpl', namespace=self.namespace
            )
    
    def _processar_itens(self, nfe_element: etree.Element, nota_fiscal: NotaFiscal) -> bool:
        """Processa itens da NFe"""
        inf_nfe = UtilXML.encontrar_elemento(nfe_element, 'infNFe', self.namespace)
        itens_det = UtilXML.encontrar_todos_elementos(inf_nfe, 'det', self.namespace)
        
        if not itens_det:
            nota_fiscal.adicionar_erro_validacao("Nenhum item encontrado na nota fiscal")
            return False
        
        for det in itens_det:
            item = self._processar_item_individual(det, nota_fiscal)
            if item:
                nota_fiscal.adicionar_item(item)
        
        if not nota_fiscal.itens:
            nota_fiscal.adicionar_erro_validacao("Nenhum item válido processado")
            return False
        
        return True
    
    def _processar_item_individual(self, det_element: etree.Element, nota_fiscal: NotaFiscal) -> Optional[ItemNotaFiscal]:
        """Processa um item individual da NFe"""
        try:
            item = ItemNotaFiscal()
            
            # Número do item
            item.numero = int(det_element.get('nItem', '0'))
            
            # Dados do produto
            prod = UtilXML.encontrar_elemento(det_element, 'prod', self.namespace)
            if prod is None:
                self._log_aviso(f"Elemento prod não encontrado no item {item.numero}")
                return None
            
            item.codigo = UtilXML.obter_texto_elemento(prod, 'cProd', namespace=self.namespace)
            item.ean = UtilXML.obter_texto_elemento(prod, 'cEAN', namespace=self.namespace)
            item.descricao = UtilXML.obter_texto_elemento(prod, 'xProd', namespace=self.namespace)
            item.ncm = UtilXML.obter_texto_elemento(prod, 'NCM', namespace=self.namespace)
            item.cest = UtilXML.obter_texto_elemento(prod, 'CEST', namespace=self.namespace)
            item.cfop = UtilXML.obter_texto_elemento(prod, 'CFOP', namespace=self.namespace)
            item.unidade = UtilXML.obter_texto_elemento(prod, 'uCom', namespace=self.namespace)
            
            # Validações básicas
            if not item.codigo:
                item.adicionar_erro_validacao("Código do produto não encontrado")
            
            if not item.descricao:
                item.adicionar_erro_validacao("Descrição do produto não encontrada")
            
            if item.ncm and not self.validador.validar_ncm(item.ncm):
                item.adicionar_erro_validacao("NCM inválido")
            
            if item.cfop and not self.validador.validar_cfop(item.cfop):
                item.adicionar_erro_validacao("CFOP inválido")
            
            # Valores comerciais
            item.quantidade = converter_para_decimal(
                UtilXML.obter_texto_elemento(prod, 'qCom', "0", self.namespace)
            )
            item.valor_unitario = converter_para_decimal(
                UtilXML.obter_texto_elemento(prod, 'vUnCom', "0", self.namespace)
            )
            item.valor_bruto = converter_para_decimal(
                UtilXML.obter_texto_elemento(prod, 'vProd', "0", self.namespace)
            )
            item.valor_desconto = converter_para_decimal(
                UtilXML.obter_texto_elemento(prod, 'vDesc', "0", self.namespace)
            )
            
            # Calcular valor total
            item.calcular_valor_total()
            
            # Processar impostos
            self._processar_impostos_item(det_element, item)
            
            # Classificar tributação
            self._classificar_tributacao_item(item)
            
            return item
            
        except Exception as e:
            self._log_erro(f"Erro ao processar item: {e}")
            return None
    
    def _processar_impostos_item(self, det_element: etree.Element, item: ItemNotaFiscal):
        """Processa impostos do item"""
        imposto = UtilXML.encontrar_elemento(det_element, 'imposto', self.namespace)
        if imposto is None:
            return
        
        # Processar PIS
        pis_element = UtilXML.encontrar_elemento(imposto, 'PIS', self.namespace)
        if pis_element is not None:
            self._processar_pis_item(pis_element, item)
        
        # Processar COFINS
        cofins_element = UtilXML.encontrar_elemento(imposto, 'COFINS', self.namespace)
        if cofins_element is not None:
            self._processar_cofins_item(cofins_element, item)
    
    def _processar_pis_item(self, pis_element: etree.Element, item: ItemNotaFiscal):
        """Processa PIS do item"""
        # Buscar em diferentes subgrupos de PIS
        subgrupos = ['PISAliq', 'PISQtde', 'PISNT', 'PISOutr']
        
        for subgrupo in subgrupos:
            pis_info = UtilXML.encontrar_elemento(pis_element, subgrupo, self.namespace)
            if pis_info is not None:
                item.pis_cst = UtilXML.obter_texto_elemento(pis_info, 'CST', namespace=self.namespace)
                item.pis_base_calculo = converter_para_decimal(
                    UtilXML.obter_texto_elemento(pis_info, 'vBC', "0", self.namespace)
                )
                item.pis_aliquota = converter_para_decimal(
                    UtilXML.obter_texto_elemento(pis_info, 'pPIS', "0", self.namespace)
                )
                item.pis_valor = converter_para_decimal(
                    UtilXML.obter_texto_elemento(pis_info, 'vPIS', "0", self.namespace)
                )
                item.pis_subgrupo = subgrupo
                
                # Validar CST
                if item.pis_cst and not self.validador.validar_cst(item.pis_cst):
                    item.adicionar_erro_validacao("CST PIS inválido")
                
                break
    
    def _processar_cofins_item(self, cofins_element: etree.Element, item: ItemNotaFiscal):
        """Processa COFINS do item"""
        # Buscar em diferentes subgrupos de COFINS
        subgrupos = ['COFINSAliq', 'COFINSQtde', 'COFINSNT', 'COFINSOutr']
        
        for subgrupo in subgrupos:
            cofins_info = UtilXML.encontrar_elemento(cofins_element, subgrupo, self.namespace)
            if cofins_info is not None:
                item.cofins_cst = UtilXML.obter_texto_elemento(cofins_info, 'CST', namespace=self.namespace)
                item.cofins_base_calculo = converter_para_decimal(
                    UtilXML.obter_texto_elemento(cofins_info, 'vBC', "0", self.namespace)
                )
                item.cofins_aliquota = converter_para_decimal(
                    UtilXML.obter_texto_elemento(cofins_info, 'pCOFINS', "0", self.namespace)
                )
                item.cofins_valor = converter_para_decimal(
                    UtilXML.obter_texto_elemento(cofins_info, 'vCOFINS', "0", self.namespace)
                )
                item.cofins_subgrupo = subgrupo
                
                # Validar CST
                if item.cofins_cst and not self.validador.validar_cst(item.cofins_cst):
                    item.adicionar_erro_validacao("CST COFINS inválido")
                
                break
    
    def _classificar_tributacao_item(self, item: ItemNotaFiscal):
        """
        Classifica tributação do item seguindo metodologia híbrida
        Prioriza NCM (conforme Mecanismo V2), mas também considera CST
        """
        # Estratégia 1: Classificação por NCM (prioritária)
        if item.ncm and self._verificar_ncm_monofasico(item.ncm):
            item.eh_monofasico_por_ncm = True
            item.tipo_tributario = "Monofasico"
            return
        
        # Estratégia 2: Classificação por CST (secundária)
        if UtilTributario.eh_produto_monofasico_por_cst(item.pis_cst, item.cofins_cst):
            item.eh_monofasico_por_cst = True
            item.tipo_tributario = "Monofasico"
            return
        
        # Se não for monofásico por nenhum critério
        item.tipo_tributario = "NaoMonofasico"
    
    def _verificar_ncm_monofasico(self, ncm: str) -> bool:
        """
        Verifica se NCM é monofásico usando tabela de referência
        """
        if not self.tabela_ncm_monofasico:
            return False
        
        # Buscar NCM exato na tabela
        return ncm in self.tabela_ncm_monofasico
    
    def _validar_consistencia_nota(self, nota_fiscal: NotaFiscal):
        """Valida consistência da nota fiscal"""
        # Validar se total de itens bate com total da nota
        valor_calculado = sum(item.valor_total for item in nota_fiscal.itens)
        diferenca = abs(valor_calculado - nota_fiscal.valor_total_nf)
        
        # Tolerância de R$ 0,01 para diferenças de arredondamento
        if diferenca > Decimal('0.01'):
            nota_fiscal.adicionar_erro_validacao(
                f"Divergência entre valor calculado ({valor_calculado}) e valor da nota ({nota_fiscal.valor_total_nf})"
            )
        
        # Validar se há pelo menos um item válido
        itens_validos = [item for item in nota_fiscal.itens if item.valido]
        if not itens_validos:
            nota_fiscal.adicionar_erro_validacao("Nenhum item válido encontrado na nota")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do processamento"""
        return self.estatisticas.copy()
    
    def limpar_estatisticas(self):
        """Limpa estatísticas do processamento"""
        self.estatisticas = {
            'total_processados': 0,
            'total_validos': 0,
            'total_invalidos': 0,
            'total_cancelados': 0
        }
    
    def _log_info(self, mensagem: str):
        """Log de informação"""
        logger.info(mensagem)
        self.logs_processamento.append(f"[INFO] {mensagem}")
    
    def _log_aviso(self, mensagem: str):
        """Log de aviso"""
        logger.warning(mensagem)
        self.logs_processamento.append(f"[WARNING] {mensagem}")
    
    def _log_erro(self, mensagem: str):
        """Log de erro"""
        logger.error(mensagem)
        self.logs_processamento.append(f"[ERROR] {mensagem}")

# Função de conveniência para usar o parser
def processar_xml_nfe_hibrido(xml_content: Union[str, bytes], 
                            tabela_ncm_monofasico: Optional[Dict] = None,
                            arquivo_origem: str = "") -> Optional[NotaFiscal]:
    """
    Função de conveniência para processar um XML de NFe
    """
    parser = NFEParserHibrido(tabela_ncm_monofasico)
    return parser.processar_xml_nfe(xml_content, arquivo_origem)

# Função para processar diretório
def processar_diretorio_nfe_hibrido(diretorio: str, 
                                  tabela_ncm_monofasico: Optional[Dict] = None,
                                  incluir_cancelamentos: bool = True) -> Dict[str, Any]:
    """
    Função de conveniência para processar diretório de XMLs
    """
    parser = NFEParserHibrido(tabela_ncm_monofasico)
    return parser.processar_diretorio(diretorio, incluir_cancelamentos)
