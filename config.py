"""Configuration for the Urabá job scraper."""

# ── Request Settings ──────────────────────────────────────────────
REQUEST_TIMEOUT = 15
RETRY_ATTEMPTS = 2
POLITE_DELAY = 1.5  # seconds between requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# ── Urabá Municipalities ─────────────────────────────────────────
URABA_MUNICIPALITIES = {
    "Apartadó":           ["apartado", "apartadó", "apartad"],
    "Turbo":              ["turbo"],
    "Carepa":             ["carepa"],
    "Chigorodó":          ["chigorodó", "chigorodo", "chigorod"],
    "Necoclí":            ["necoclí", "necocli", "necocl"],
    "Arboletes":          ["arboletes"],
    "San Juan de Urabá":  ["san juan de uraba", "san juan de urabá"],
    "San Pedro de Urabá": ["san pedro de uraba", "san pedro de urabá"],
    "Mutatá":             ["mutatá", "mutata"],
    "Murindó":            ["murindó", "murindo"],
    "Vigía del Fuerte":   ["vigía del fuerte", "vigia del fuerte"],
    "Dabeiba":            ["dabeiba"],
}

# ── Urabá-specific search terms for each portal ──────────────────
SEARCH_LOCATIONS = [
    "apartado",
    "turbo-antioquia",
    "carepa",
    "chigorodo",
    "uraba",
]

# ── Contract Type Keywords ────────────────────────────────────────
TEMPORAL_KEYWORDS = [
    "temporal", "obra o labor", "prestación de servicios",
    "freelance", "contrato por obra", "tiempo parcial",
    "medio tiempo", "part-time", "proyecto", "pasantía",
    "practicante", "aprendiz", "suplencia",
]

PERMANENT_KEYWORDS = [
    "indefinido", "término indefinido", "planta",
    "permanente", "fijo", "tiempo completo", "full-time",
    "contrato a término indefinido",
]

# ── Benefits Keywords ─────────────────────────────────────────────
BENEFITS_MAP = {
    "Salud/EPS":        ["salud", "eps", "arl", "seguridad social"],
    "Pensión":          ["pensión", "pension", "fondo de pensiones"],
    "Bonificación":     ["bonificación", "bonificacion", "prima", "bono"],
    "Horario flexible": ["horario flexible", "flexible"],
    "Teletrabajo":      ["home office", "remoto", "teletrabajo", "trabajo remoto"],
    "Transporte":       ["transporte", "movilidad", "auxilio de transporte"],
    "Alimentación":     ["alimentación", "alimentacion", "almuerzo", "casino"],
    "Capacitación":     ["capacitación", "capacitacion", "formación", "curso"],
    "Comisiones":       ["comisión", "comision", "comisiones", "variable"],
}

# ── Relevance Scoring ─────────────────────────────────────────────
STRONG_RELEVANCE_KEYWORDS = [
    "apartadó", "apartado", "turbo", "urabá", "uraba",
    "carepa", "chigorodó", "chigorodo", "necoclí", "necocli",
    "arboletes", "mutatá", "mutata", "dabeiba",
    "zona bananera", "eje bananero",
]

MEDIUM_RELEVANCE_KEYWORDS = [
    "antioquia", "colombia",
]

NEGATIVE_RELEVANCE_KEYWORDS = [
    "bogotá", "bogota", "medellín", "medellin", "cali",
    "barranquilla", "cartagena", "bucaramanga",
]
