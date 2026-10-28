from typing import Any, Dict, Optional
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...validators.cpf import validate_cpf, mask_cpf, format_cpf

# 9º dígito do CPF indica a Região Fiscal emissora original
REGIOES_FISCAIS = {
    "1": "1ª Região Fiscal (DF, GO, MS, MT, TO)",
    "2": "2ª Região Fiscal (AC, AM, AP, PA, RO, RR)",
    "3": "3ª Região Fiscal (CE, MA, PI)",
    "4": "4ª Região Fiscal (AL, PB, PE, RN)",
    "5": "5ª Região Fiscal (BA, SE)",
    "6": "6ª Região Fiscal (MG)",
    "7": "7ª Região Fiscal (ES, RJ)",
    "8": "8ª Região Fiscal (SP)",
    "9": "9ª Região Fiscal (PR, SC)",
    "0": "10ª Região Fiscal (RS)",
}

class CpfOfficialAdapter(BaseAdapter):
    adapter_id = "cpf_official"
    name = "Receita Federal e Certidões Públicas de CPF"
    category = "cpf"
    description = "Validação algorítmica rigorosa (Módulo 11), detecção de região fiscal de origem e emissão guiada de certidões públicas oficiais."
    official_url = "https://servicos.receita.fazenda.gov.br/servicos/cpf/consultasituacao/consultapublica.asp"
    supported_inputs = ["cpf"]
    requires_captcha = True

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        is_valid, result_or_err = validate_cpf(target)
        if not is_valid:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message=result_or_err,
                confidence=ConfidenceLevel.HIGH,
            )

        clean_cpf = result_or_err
        masked = mask_cpf(clean_cpf)
        formatted = format_cpf(clean_cpf)
        nono_digito = clean_cpf[8]
        regiao_fiscal = REGIOES_FISCAIS.get(nono_digito, "Região não mapeada")

        official_links = [
            {
                "titulo": "Receita Federal - Comprovante de Situação Cadastral no CPF",
                "url": "https://servicos.receita.fazenda.gov.br/servicos/cpf/consultasituacao/consultapublica.asp",
                "descricao": "Consulta oficial da regularidade cadastral (Regular, Suspensa, Cancelada). Exige data de nascimento e CAPTCHA para preservação da privacidade.",
                "requer": "Data de nascimento e resolução de CAPTCHA",
            },
            {
                "titulo": "PGFN / Receita Federal - Certidão Negativa de Débitos Federais",
                "url": "https://solucoes.receita.fazenda.gov.br/servicos/certidaointernet/pf/emitir",
                "descricao": "Emissão de Certidão Negativa (CND) de tributos federais e dívida ativa.",
                "requer": "Apenas o CPF e resolução de CAPTCHA oficial",
            },
            {
                "titulo": "TSE - Certidão de Quitação Eleitoral",
                "url": "https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-quitacao-eleitoral",
                "descricao": "Verificação de quitação e regularidade com a Justiça Eleitoral.",
                "requer": "Nome completo, data de nascimento e filiação",
            },
            {
                "titulo": "TST - Certidão Negativa de Débitos Trabalhistas (CNDT)",
                "url": "https://cndt-certidao.tst.jus.br/gerarCertidao.faces",
                "descricao": "Verificação de débitos perante a Justiça do Trabalho brasileira.",
                "requer": "Apenas o CPF e CAPTCHA",
            }
        ]

        normalized = {
            "cpf_mascarado": masked,
            "valido_algoritmo": True,
            "regiao_fiscal_origem": regiao_fiscal,
            "nono_digito": nono_digito,
            "portais_oficiais_para_consulta": official_links,
        }

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=ResultStatus.CONFIRMED,
            timestamp="",
            execution_time_ms=0,
            data=normalized,
            verification_url=self.official_url,
            confidence=ConfidenceLevel.HIGH,
            requires_manual_action=True,
            action_url="https://servicos.receita.fazenda.gov.br/servicos/cpf/consultasituacao/consultapublica.asp",
            limitations=[
                "LGPD e Segurança: Portais governamentais oficiais exigem data de nascimento e desafio CAPTCHA humano para emitir comprovantes cadastrais.",
                "O OSINT Brazuca Ultimate não realiza bypass de CAPTCHAs nem armazena dados privados.",
            ]
        )
