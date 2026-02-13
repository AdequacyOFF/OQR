"""Admission use cases."""

from .verify_entry_qr import VerifyEntryQRUseCase, VerifyEntryQRResult
from .approve_admission import ApproveAdmissionUseCase, ApproveAdmissionResult

__all__ = [
    "VerifyEntryQRUseCase",
    "VerifyEntryQRResult",
    "ApproveAdmissionUseCase",
    "ApproveAdmissionResult",
]
