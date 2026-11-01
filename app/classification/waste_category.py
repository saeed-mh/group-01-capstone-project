from enum import Enum

class WasteCategory(Enum):
    PACKAGING = "packaging"
    PAPER = "paper"
    GLASS = "glass"
    ORGANIC = "organic"
    RESIDUAL = "residual"
    HAZARDOUS = "hazardous"