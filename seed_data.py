#!/usr/bin/env python3
"""
Seed jobs.json with real job data collected from web search results.
Run this when direct HTTP scraping is blocked (e.g., sandbox/proxy environments).
The main scrapers (main.py) are the primary method for your own machine.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_schema import JobPosting
from processing import DataCleaner
from dashboard import DashboardGenerator

# ── Real job data extracted from web search results (Feb 2026) ────

RAW_JOBS = [
    # ── elempleo.com ──────────────────────────────────────────────
    {
        "title": "Asesor de Servicios",
        "company": "Confiar Cooperativa Financiera",
        "location": "Apartadó, Antioquia (cubre Dabeiba, Caucasia, Turbo, Quibdó)",
        "salary_raw": "$2.761.000 + incentivos + beneficios extralegales",
        "description": "Asesor de servicios en cooperativa financiera. Contrato a término indefinido. Disponibilidad para cubrir agencias de Dabeiba, Caucasia, Apartadó, Turbo y Quibdó.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/apartado",
        "source": "elempleo.com",
        "contract_type": "permanente",
    },
    {
        "title": "Gestor Comercial",
        "company": "Incentiva",
        "location": "Apartadó, Carepa, Chigorodó",
        "salary_raw": "$2.100.000 (básico $1.700.000 + comisiones)",
        "description": "Gestor comercial apasionado por ventas. Impulsar crecimiento de marca mediante gestión de ventas directas en comercios. Aplica si estás en Apartadó, Carepa o Chigorodó.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/trabajo-apartado",
        "source": "elempleo.com",
    },
    {
        "title": "Asesor Comercial Sector Financiero",
        "company": "Entidad Financiera (Great Place to Work)",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.423.500 + auxilio transporte $200.000 + comisiones promedio $2.000.000 a $2.500.000",
        "description": "Asesor comercial sector financiero. Salario base $1.423.500, auxilio de transporte $200.000, comisiones sin techo y 100% prestacionales. Pago quincenal. Horario lunes a sábado + 2 domingos al mes. Requiere 6 meses experiencia en ventas intangibles.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/apartado",
        "source": "elempleo.com",
    },
    {
        "title": "Psicólogo(a) Bienestar Institucional",
        "company": "Institución Universitaria",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.590.584",
        "description": "Psicólogo(a) con especialización clínica, 1 a 2 años de experiencia en bienestar institucional y comunidad universitaria. Medio tiempo. Contrato fijo.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/apartado",
        "source": "elempleo.com",
        "contract_type": "temporal",
    },
    {
        "title": "Director de Gestión Humana",
        "company": "Empresa constructora infraestructura vial",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir (profesional senior)",
        "description": "Director de gestión humana para empresa constructora de infraestructura vial. Título profesional en administración, Psicología o Ingeniería Industrial. Especialización en RRHH. Mínimo 5 años experiencia general, 3 años liderando gestión humana en infraestructura vial.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/apartado",
        "source": "elempleo.com",
    },
    {
        "title": "Ingeniero Agrónomo",
        "company": "Empresa agrícola",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Ingeniero agrónomo con especialización en proyectos, productividad o afines. Generar y validar plan de trabajo en fincas: nutrición, manejo integrado de plagas y enfermedades, programas de intervención.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/apartado",
        "source": "elempleo.com",
    },
    {
        "title": "Gestor de Acompañamiento",
        "company": "AGS Colombia",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$110.000 por paciente acompañado",
        "description": "Empresa de consultoría e interventoría del sector salud requiere Auxiliar de Enfermería con mínimo 6 meses de experiencia. Contrato prestación de servicios.",
        "url": "https://www.elempleo.com/co/ofertas-empleo/apartado",
        "source": "elempleo.com",
        "contract_type": "temporal",
    },
    {
        "title": "Auxiliar Administrativo / Facturación",
        "company": "Empresa sector industrial",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.785.130",
        "description": "Auxiliar administrativo y de facturación. Contrato a término indefinido. Lunes a viernes.",
        "url": "https://co.jooble.org/trabajo-lunes-viernes/Apartadó,-Antioquia",
        "source": "Jooble",
        "contract_type": "permanente",
    },

    # ── Computrabajo ──────────────────────────────────────────────
    {
        "title": "Asesor Comercial",
        "company": "NEXA BPO",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$4.000.000 + comisiones",
        "description": "Asesor comercial con experiencia en ventas. Salario $4.000.000 mensuales más comisiones.",
        "url": "https://co.computrabajo.com/empleos-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Conductor de Vehículo",
        "company": "Empresa Transportadora San Gabriel SAS",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.750.905",
        "description": "Conductor de vehículo para empresa transportadora.",
        "url": "https://co.computrabajo.com/empleos-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Asesor Comercial Agrícola",
        "company": "Empresa sector agrícola",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.800.000 + comisiones",
        "description": "Asesor comercial en sector agrícola. Salario mensual más comisiones.",
        "url": "https://co.computrabajo.com/empleos-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Coordinador de Calidad",
        "company": "Dar Ayuda Temporal",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$3.000.000",
        "description": "Coordinador de calidad para empresa temporal. Salario $3.000.000 mensuales.",
        "url": "https://co.computrabajo.com/empleos-en-apartado",
        "source": "Computrabajo",
        "contract_type": "temporal",
    },
    {
        "title": "Supervisor de Seguridad",
        "company": "PREVENTUS SAS",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$3.800.000",
        "description": "Supervisor de seguridad para empresa de vigilancia.",
        "url": "https://co.computrabajo.com/empleos-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Vigilante de Seguridad",
        "company": "SVS – Seguridad y Vigilancia Serviconcel Ltda.",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.750.900",
        "description": "Vigilante de seguridad privada.",
        "url": "https://co.computrabajo.com/empleos-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Asesor Comercial Financiero",
        "company": "UNI2 Microcrédito",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$2.000.000 + comisiones",
        "description": "Asesor comercial para microcrédito. Salario base más comisiones.",
        "url": "https://co.computrabajo.com/trabajo-de-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Coordinador Logístico",
        "company": "PROSEGUR Gestión de Activos Colombia SAS",
        "location": "Apartadó, Antioquia",
        "salary_raw": "Urgente - a convenir",
        "description": "Coordinador logístico. Vacante urgente.",
        "url": "https://co.computrabajo.com/trabajo-de-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Asesor Comercial Veterinario",
        "company": "GABRICA S.A.S.",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Asesor comercial para empresa de productos veterinarios.",
        "url": "https://co.computrabajo.com/trabajo-de-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Auxiliar Operativo",
        "company": "Adecco Colombia S.A.",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.615.400",
        "description": "Auxiliar operativo para empresa temporal.",
        "url": "https://co.computrabajo.com/trabajo-de-apartado",
        "source": "Computrabajo",
        "contract_type": "temporal",
    },
    {
        "title": "Operario de Producción",
        "company": "Mision Empresarial S.A",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.423.500",
        "description": "Operario de producción. Salario mínimo. Contrato a término fijo. Jornada lunes a sábado.",
        "url": "https://co.computrabajo.com/trabajo-de-apartado",
        "source": "Computrabajo",
        "contract_type": "temporal",
    },
    {
        "title": "Asesor Comercial Telecomunicaciones",
        "company": "MEGALINEA S.A",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$2.346.000",
        "description": "Asesor comercial en telecomunicaciones.",
        "url": "https://co.computrabajo.com/trabajo-de-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Auxiliar de Bodega",
        "company": "Pisos & Enchapes RYL SAS",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.850.000",
        "description": "Auxiliar de bodega para empresa de pisos y enchapes.",
        "url": "https://co.computrabajo.com/empleos-en-apartado?p=2",
        "source": "Computrabajo",
    },
    {
        "title": "Operario de Producción",
        "company": "Sero S.A.S.",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.480.500",
        "description": "Operario de producción en empresa industrial.",
        "url": "https://co.computrabajo.com/empleos-en-apartado?p=2",
        "source": "Computrabajo",
    },
    {
        "title": "Médico General Urgencias",
        "company": "Médicos del Mundo (Médecins du Monde)",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$6.968.700",
        "description": "Médico general para urgencias. Organización internacional de salud.",
        "url": "https://co.computrabajo.com/trabajo-de-profesional-con-conocimientos-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Coordinador Comercial Regional",
        "company": "ORIENTTE S.A.S.",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$5.000.000",
        "description": "Coordinador comercial regional. Empresa de servicios.",
        "url": "https://co.computrabajo.com/trabajo-de-antioquia-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Asesor de Empleo",
        "company": "Agencia de Empleo COMFAMA",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$3.000.000",
        "description": "Asesor de empleo para agencia de Comfama en Urabá.",
        "url": "https://co.computrabajo.com/trabajo-de-antioquia-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Vendedor Preventa",
        "company": "Manpower Group Colombia",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.800.000",
        "description": "Vendedor de preventa. Salario mensual.",
        "url": "https://co.computrabajo.com/trabajo-de-antioquia-en-apartado",
        "source": "Computrabajo",
    },
    {
        "title": "Auxiliar de Droguería",
        "company": "Droguerías y Farmacias Cruz Verde S.A.S.",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.423.500",
        "description": "Auxiliar de droguería. Sin experiencia requerida. Salario mínimo.",
        "url": "https://co.computrabajo.com/empleos-en-apartado-sin-experiencia",
        "source": "Computrabajo",
    },
    {
        "title": "Supervisor de Seguridad",
        "company": "Seguridad Atempi de Colombia Ltda",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$2.400.000",
        "description": "Supervisor de seguridad privada.",
        "url": "https://co.computrabajo.com/empleos-de-servicios-generales-aseo-y-seguridad-en-apartado",
        "source": "Computrabajo",
    },

    # ── Comfama Urabá ─────────────────────────────────────────────
    {
        "title": "Técnico Mecánico Automotriz",
        "company": "Empresa automotriz (via Comfama)",
        "location": "Urabá, Antioquia",
        "salary_raw": "$1.102.482 + prestaciones sociales",
        "description": "Técnico mecánico automotriz con o sin experiencia pero con curso certificado en revisión técnico mecánica (155 horas). Contrato término indefinido. Lunes a sábado.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
        "contract_type": "permanente",
    },
    {
        "title": "Profesional en Fisioterapia",
        "company": "Empresa deportiva (via Comfama)",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.048.712 + prestaciones legales",
        "description": "Profesional en fisioterapia con mínimo 6 meses de experiencia en campo deportivo. Contrato término indefinido. Medio tiempo. Lunes a sábados.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/apartado/",
        "source": "Comfama",
        "contract_type": "permanente",
    },
    {
        "title": "Aprendiz / Practicante",
        "company": "Empresa agroindustrial (via Comfama)",
        "location": "Chigorodó, Antioquia",
        "salary_raw": "$877.803 (apoyo de sostenimiento)",
        "description": "Vacante en Chigorodó, Vereda la Fe. Apoyo de sostenimiento.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/chigorodo/",
        "source": "Comfama",
        "contract_type": "temporal",
    },
    {
        "title": "Cajero / Atención al Cliente",
        "company": "Empresa comercial (via Comfama)",
        "location": "Necoclí, Antioquia",
        "salary_raw": "SMMLV + prestaciones sociales",
        "description": "Bachiller con mínimo 1 año de experiencia en manejo de caja, apertura, cierre y servicio al cliente. Debe residir en Necoclí. Contrato término fijo. Tiempo completo.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
        "contract_type": "temporal",
    },
    {
        "title": "Profesional en Psicología o Trabajo Social",
        "company": "Empresa social (via Comfama)",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Profesional en psicología o trabajo social con mínimo 3 años de experiencia. Contrato término fijo. Tiempo completo.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
        "contract_type": "temporal",
    },
    {
        "title": "Gestor(a) Empresarial Convenio Incentivos",
        "company": "Comfama",
        "location": "Urabá, Antioquia",
        "salary_raw": "Competitivo + 4 primas extralegales (95 días adicionales de salario/año)",
        "description": "Acompañar y fidelizar empresas usuarias del servicio de empleo. Fortalecer ecosistema laboral del Urabá. Beneficios: 4 primas extralegales, acceso a ~80 beneficios en educación, vivienda, salud, turismo.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
        "contract_type": "permanente",
    },

    # ── Indeed / Jooble / LinkedIn ────────────────────────────────
    {
        "title": "Operario de Producción (Aguacates)",
        "company": "Misión Empresarial",
        "location": "Urabá, Antioquia",
        "salary_raw": "$1.423.500",
        "description": "Hombres y mujeres con o sin experiencia. Selección y manipulación, empaque, etiquetado, sellado, rotulado, cargue, descargue en empresa exportadora de aguacates.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
        "contract_type": "temporal",
    },
    {
        "title": "Operario Supernumerario de Producción",
        "company": "Empresa sector industrial",
        "location": "Carepa, Antioquia",
        "salary_raw": "SMMLV + prestaciones",
        "description": "Técnico en mantenimiento industrial, electrónica, electricidad o calidad/alimentos. Mínimo 6 meses experiencia.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
        "contract_type": "temporal",
    },
    {
        "title": "Operario de Producción y Despachos",
        "company": "Empresa de construcción",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Experiencia mínima 1 año en construcción. Selección y clasificación de ladrillo para garantizar calidad.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
    },
    {
        "title": "Auxiliar de Transporte / Logística",
        "company": "Empresa sector industrial",
        "location": "Urabá, Antioquia",
        "salary_raw": "A convenir",
        "description": "Auxiliar de transporte con experiencia mínima 1 año en procesos logísticos. Coordinar asignación de conductores y vehículos.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
    },
    {
        "title": "Auxiliar de Empacadora (Banano)",
        "company": "Empresa sector agrícola",
        "location": "Urabá, Antioquia",
        "salary_raw": "A convenir",
        "description": "Auxiliar de empacadora con experiencia mínima 1 año en labores bananeras.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
    },
    {
        "title": "Auxiliar de Saneamiento y Ambiente",
        "company": "Empresa sector agrícola",
        "location": "Urabá, Antioquia",
        "salary_raw": "A convenir",
        "description": "Experiencia mínima 3 años en mantenimiento de plantas de aguas residuales y potable.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
    },
    {
        "title": "Auxiliar de Mercado Nacional (Banano)",
        "company": "Empresa bananera",
        "location": "Urabá, Antioquia",
        "salary_raw": "A convenir",
        "description": "Experiencia mínima 1 año en comercialización sector agrícola, preferiblemente empresas bananeras.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
    },
    {
        "title": "Despachador de Contenedores",
        "company": "Puerto Bahía Colombia",
        "location": "Turbo, Antioquia",
        "salary_raw": "A convenir",
        "description": "Despachador de contenedores con experiencia mínima 1 año en manejo de sistemas operativos de terminales y equipos portuarios.",
        "url": "https://co.indeed.com/Empleos-en-Urabá,-Antioquia",
        "source": "Indeed",
    },
    {
        "title": "Cajero Bancario",
        "company": "Banco de Occidente",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Cajero para sucursal en Apartadó. Operador de caja y atención al cliente.",
        "url": "https://co.linkedin.com/jobs/empleos-en-apartadó",
        "source": "LinkedIn",
    },
    {
        "title": "Asesor(a) Comercial Moda",
        "company": "Hogar y Moda SAS",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Asesor(a) tienda de moda con contratación inmediata.",
        "url": "https://co.linkedin.com/jobs/empleos-en-apartadó",
        "source": "LinkedIn",
    },
    {
        "title": "Auxiliar Administrativa Finca - Supernumeraria",
        "company": "Empresa agrícola",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Auxiliar administrativa para finca. Puesto supernumerario.",
        "url": "https://co.linkedin.com/jobs/empleos-en-apartadó",
        "source": "LinkedIn",
    },
    {
        "title": "Auxiliar de Control de Pérdidas",
        "company": "Empresa comercial",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Auxiliar de control de pérdidas en establecimiento comercial.",
        "url": "https://co.linkedin.com/jobs/empleos-en-apartadó",
        "source": "LinkedIn",
    },
    {
        "title": "Auxiliar de Ventas",
        "company": "Empresa comercial",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Auxiliar de ventas. Sin experiencia requerida.",
        "url": "https://co.linkedin.com/jobs/empleos-en-apartadó",
        "source": "LinkedIn",
    },
    {
        "title": "Auxiliar Operativo de Tienda",
        "company": "Cadena retail",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.432.600 + auxilio de transporte",
        "description": "Auxiliar operativo de tienda. Jornada de 36 horas al mes.",
        "url": "https://co.jooble.org/trabajo-lunes-viernes/Apartadó,-Antioquia",
        "source": "Jooble",
        "contract_type": "temporal",
    },
    {
        "title": "Operario de Producción",
        "company": "Empresa industrial",
        "location": "Apartadó, Antioquia",
        "salary_raw": "$1.423.500",
        "description": "Operario de producción. Contrato término fijo. Jornada lunes a sábado.",
        "url": "https://co.jooble.org/trabajo-lunes-viernes/Apartadó,-Antioquia",
        "source": "Jooble",
        "contract_type": "temporal",
    },

    # ── Comfenalco Urabá ─────────────────────────────────────────
    {
        "title": "Auxiliar Comercial",
        "company": "Empresa comercial (via Comfenalco)",
        "location": "Carepa, Antioquia",
        "salary_raw": "A convenir",
        "description": "Auxiliar comercial. Contrato término fijo. Jornada diurna. Mínimo 2 años experiencia. Requiere certificación en manipulación de alimentos.",
        "url": "https://www.comfenalcoantioquia.com.co/personas/sedes/oficina-de-empleo-apartado",
        "source": "Comfenalco",
        "contract_type": "temporal",
    },
    {
        "title": "Supervisor Logístico",
        "company": "Empresa logística (via Comfenalco)",
        "location": "Turbo, Antioquia",
        "salary_raw": "A convenir",
        "description": "Supervisor logístico para zona de Turbo. Contrato término fijo.",
        "url": "https://www.comfenalcoantioquia.com.co/personas/sedes/oficina-de-empleo-apartado",
        "source": "Comfenalco",
        "contract_type": "temporal",
    },
    {
        "title": "Coordinador de Calidad",
        "company": "Empresa agroindustrial (via Comfenalco)",
        "location": "Chigorodó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Coordinador de calidad para empresa agroindustrial.",
        "url": "https://www.comfenalcoantioquia.com.co/personas/sedes/oficina-de-empleo-apartado",
        "source": "Comfenalco",
    },
    {
        "title": "Tallerista Educativo",
        "company": "Entidad educativa (via Comfenalco)",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Tallerista educativo para programas de primera infancia.",
        "url": "https://www.comfenalcoantioquia.com.co/personas/sedes/oficina-de-empleo-apartado",
        "source": "Comfenalco",
    },
    {
        "title": "Cajero(a)",
        "company": "Empresa comercial (via Comfenalco)",
        "location": "Turbo, Antioquia",
        "salary_raw": "SMMLV",
        "description": "Cajero(a) para establecimiento comercial en Turbo.",
        "url": "https://www.comfenalcoantioquia.com.co/personas/sedes/oficina-de-empleo-apartado",
        "source": "Comfenalco",
    },
    {
        "title": "Aprendiz de Primera Infancia",
        "company": "Entidad educativa (via Comfenalco)",
        "location": "Carepa, Antioquia",
        "salary_raw": "Apoyo de sostenimiento",
        "description": "Aprendiz en programa de primera infancia.",
        "url": "https://www.comfenalcoantioquia.com.co/personas/sedes/oficina-de-empleo-apartado",
        "source": "Comfenalco",
        "contract_type": "temporal",
    },

    # ── Magneto365 / Mitula ───────────────────────────────────────
    {
        "title": "Preventa Comercial",
        "company": "Empresa de consumo masivo",
        "location": "Chigorodó, Carepa, Apartadó, Turbo, Necoclí",
        "salary_raw": "A convenir",
        "description": "Prevender productos de la compañía en Chigorodó, Carepa, Apartadó, Turbo y Necoclí.",
        "url": "https://www.magneto365.com/co/trabajos/ofertas-empleo-en-apartado",
        "source": "Magneto365",
    },
    {
        "title": "Médico General",
        "company": "CIS Urabá",
        "location": "Apartadó, Chigorodó, Carepa, Turbo",
        "salary_raw": "A convenir",
        "description": "Médico general para Centros de Investigación en Salud en Urabá: Apartadó, Chigorodó, Carepa, Turbo, Nueva Colonia, Currulao.",
        "url": "https://www.magneto365.com/co/trabajos/ofertas-empleo-en-apartado",
        "source": "Magneto365",
    },
    {
        "title": "Auxiliar de Bodega",
        "company": "Empresa industrial",
        "location": "Chigorodó, Antioquia",
        "salary_raw": "$1.105.000",
        "description": "Auxiliar de bodega en Chigorodó.",
        "url": "https://empleo.mitula.com.co/empleo/chigorodo-antioquia",
        "source": "Magneto365",
    },
    {
        "title": "Coordinador de Bodega",
        "company": "Empresa logística",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Coordinador de bodega. Experiencia en logística y almacenamiento.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
    },
    {
        "title": "Ingeniero Residente de Obra",
        "company": "Empresa constructora",
        "location": "Turbo, Antioquia",
        "salary_raw": "A convenir (profesional)",
        "description": "Ingeniero residente de obra para proyecto de infraestructura vial.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
    },
    {
        "title": "Administrador de Finca",
        "company": "Empresa agrícola",
        "location": "Urabá, Antioquia",
        "salary_raw": "A convenir",
        "description": "Administrador de finca en zona rural de Urabá.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
    },
    {
        "title": "Conductor de Vehículo de Carga",
        "company": "Empresa de transporte",
        "location": "Carepa, Antioquia",
        "salary_raw": "A convenir",
        "description": "Conductor de vehículo de carga pesada.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
    },
    {
        "title": "Docente Coordinador de Psicología",
        "company": "Institución educativa",
        "location": "Apartadó, Antioquia",
        "salary_raw": "A convenir",
        "description": "Docente coordinador de psicología para institución educativa.",
        "url": "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
        "source": "Comfama",
    },
    {
        "title": "Auxiliar de Ruta",
        "company": "Empresa de distribución",
        "location": "Apartadó, Antioquia",
        "salary_raw": "SMMLV + prestaciones",
        "description": "Auxiliar de ruta sin experiencia.",
        "url": "https://co.linkedin.com/jobs/empleos-en-apartadó",
        "source": "LinkedIn",
    },
]


def main():
    print("Seeding job data from web search results...")

    jobs = []
    for raw in RAW_JOBS:
        job = JobPosting(
            title=raw["title"],
            company=raw["company"],
            location=raw["location"],
            salary_raw=raw.get("salary_raw", ""),
            description=raw.get("description", ""),
            url=raw.get("url", ""),
            source=raw.get("source", ""),
        )
        # Pre-set contract type if known
        if "contract_type" in raw:
            job.contract_type = raw["contract_type"]
            job.is_temporal = raw["contract_type"] == "temporal"
        jobs.append(job)

    print(f"  Raw jobs: {len(jobs)}")

    # Run through cleaning pipeline
    cleaned = DataCleaner.clean_all(jobs)
    print(f"  After cleaning: {len(cleaned)}")

    # Save JSON
    output_dir = Path(__file__).resolve().parent
    json_path = output_dir / "jobs.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            [j.to_dict() for j in cleaned],
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    print(f"  Saved → {json_path}")

    # Generate dashboard
    dashboard_path = output_dir / "dashboard.html"
    gen = DashboardGenerator(cleaned)
    gen.generate(str(dashboard_path))
    print(f"  Dashboard → {dashboard_path}")

    # Summary
    from collections import Counter
    zones = Counter(j.zone for j in cleaned)
    sources = Counter(j.source for j in cleaned)
    contracts = Counter(j.contract_type for j in cleaned)

    print(f"\n  By zone:     {dict(zones.most_common(10))}")
    print(f"  By source:   {dict(sources.most_common())}")
    print(f"  By contract: {dict(contracts.most_common())}")
    print("\nDone!")


if __name__ == "__main__":
    main()
