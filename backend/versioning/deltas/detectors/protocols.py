# versioning/deltas/detectors/protocols.py
from typing import Any, Dict, List, Protocol, TypeVar

# La variable de tipo sigue siendo útil
T_Model = TypeVar("T_Model", contravariant=True)

# Este es nuestro nuevo contrato, no hereda de nadie más que de Protocol.
# Describe la "forma" que debe tener un objeto para ser un detector de entidades
# que pueda ser procesado por nuestra función _process_collection.
class PublicFieldsDetector(Protocol[T_Model]):
    """
    Defines the contract for a detector suitable for processing collections.

    It must have both a `detect` method and a `public_field_names` property.
    """
    
    # Requisito 1: Debe tener esta propiedad
    @property
    def public_field_names(self) -> List[str]:
        ...

    # Requisito 2: Debe tener este método
    def detect(self, old: T_Model, new: T_Model) -> Dict[str, Any] | None:
        ...