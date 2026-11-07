from enum import Enum

class WasteCategory(str, Enum):

    PACKAGING = "packaging"
    PAPER = "paper"
    GLASS = "glass"
    ORGANIC = "organic"
    RESIDUAL = "residual"
    HAZARDOUS = "hazardous"
