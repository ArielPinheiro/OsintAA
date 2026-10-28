import hashlib
import mimetypes
import os
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel
from ...config import settings

def extract_jpeg_exif(data: bytes) -> Dict[str, Any]:
    """Extração leve e segura de tags básicas EXIF de imagens JPEG sem dependências pesadas."""
    exif_data = {}
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return exif_data

    idx = 2
    while idx < len(data) - 4:
        marker, length = struct.unpack(">HH", data[idx:idx+4])
        if marker == 0xffe1:  # APP1 (EXIF)
            app1_data = data[idx+4 : idx+2+length]
            if app1_data.startswith(b"Exif\x00\x00"):
                exif_data["exif_presente"] = True
                exif_data["tamanho_bloco_exif_bytes"] = length
            break
        elif (marker & 0xff00) != 0xff00 or marker == 0xffda:
            break
        idx += 2 + length

    return exif_data

class DocumentAnalyzerAdapter(BaseAdapter):
    adapter_id = "document_analyzer"
    name = "Analisador Forense Local de Arquivos e Metadados"
    category = "documentos"
    description = "Cálculo local de hashes criptográficos (SHA-256, SHA-1, MD5), identificação de tipo MIME, extração de metadados e checagem de integridade."
    official_url = "https://csrc.nist.gov/publications/detail/fips/180-4/final"
    supported_inputs = ["arquivo", "hash"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        context = context or {}
        file_bytes: Optional[bytes] = context.get("file_bytes")
        filename: str = context.get("filename", os.path.basename(target))

        # Se target for hash direto digitado pelo usuário
        if not file_bytes and len(target.strip()) in (32, 40, 64) and all(c in "0123456789abcdefABCDEF" for c in target.strip()):
            hash_str = target.strip().lower()
            hash_type = "MD5" if len(hash_str) == 32 else ("SHA-1" if len(hash_str) == 40 else "SHA-256")
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.CONFIRMED,
                timestamp="",
                execution_time_ms=0,
                data={
                    "tipo_entrada": "hash_direto",
                    "algoritmo_identificado": hash_type,
                    "hash_valor": hash_str,
                    "links_verificacao_inteligencia": [
                        {"nome": "VirusTotal", "url": f"https://www.virustotal.com/gui/file/{hash_str}"},
                        {"nome": "MalwareBazaar", "url": f"https://bazaar.abuse.ch/sample/{hash_str}"},
                        {"nome": "Hybrid Analysis", "url": f"https://www.hybrid-analysis.com/search?query={hash_str}"},
                    ]
                },
                confidence=ConfidenceLevel.HIGH,
                limitations=["Consulta de hash em bases públicas de reputação. O arquivo não foi enviado."]
            )

        # Se for caminho de arquivo local
        if not file_bytes and os.path.exists(target):
            # Limitar tamanho
            max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
            if os.path.getsize(target) > max_bytes:
                return SourceExecutionResult(
                    source_id=self.adapter_id,
                    source_name=self.name,
                    category=self.category,
                    status=ResultStatus.ERROR,
                    timestamp="",
                    execution_time_ms=0,
                    error_message=f"Arquivo excede o limite máximo permitido de {settings.MAX_UPLOAD_SIZE_MB}MB.",
                    confidence=ConfidenceLevel.LOW,
                )
            with open(target, "rb") as f:
                file_bytes = f.read()

        if not file_bytes:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message="Nenhum dado de arquivo válido ou hash foi fornecido para análise.",
                confidence=ConfidenceLevel.LOW,
            )

        # Cálculo de Hashes
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        sha1 = hashlib.sha1(file_bytes).hexdigest()
        md5 = hashlib.md5(file_bytes).hexdigest()
        size_bytes = len(file_bytes)

        # Tipo MIME
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"

        # EXIF em JPEG
        exif_info = extract_jpeg_exif(file_bytes)

        normalized = {
            "nome_arquivo": filename,
            "tamanho_bytes": size_bytes,
            "tamanho_legivel": f"{round(size_bytes / 1024, 2)} KB" if size_bytes < 1024*1024 else f"{round(size_bytes / (1024*1024), 2)} MB",
            "tipo_mime_detectado": mime_type,
            "hashes": {
                "sha256": sha256,
                "sha1": sha1,
                "md5": md5,
            },
            "metadados": exif_info,
            "links_verificacao_inteligencia": [
                {"nome": "VirusTotal", "url": f"https://www.virustotal.com/gui/file/{sha256}"},
                {"nome": "Hybrid Analysis", "url": f"https://www.hybrid-analysis.com/search?query={sha256}"},
                {"nome": "MalwareBazaar", "url": f"https://bazaar.abuse.ch/sample/{sha256}"},
            ]
        }

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=ResultStatus.CONFIRMED,
            timestamp="",
            execution_time_ms=0,
            data=normalized,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Processamento 100% LOCAL e confidencial.",
                "NENHUM byte ou conteúdo deste arquivo foi transmitido para a Internet.",
                "Os links de inteligência fornecidos realizam busca apenas pelo hash SHA-256 já calculado.",
            ]
        )

