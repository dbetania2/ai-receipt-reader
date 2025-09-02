Ticket App: Una API para Procesar Recibos (Versión Web)
📄 Visión General del Proyecto
Este proyecto es una aplicación web y una API de procesamiento de recibos desarrollada en Python utilizando el framework Flask. Su objetivo principal es automatizar la extracción de datos de imágenes de recibos y organizar esa información de manera estructurada en una hoja de cálculo de Google Sheets.

Esta versión es la evolución de un proyecto original de escritorio, creado en Java, y representa un esfuerzo para modernizar y extender sus funcionalidades a un entorno web accesible.

🚀 Características Clave
Procesamiento de Imágenes con IA: Utiliza la API de Google Cloud Vision para extraer texto de forma precisa desde las imágenes de los recibos.

Análisis de Datos con Gemini: Emplea el modelo de lenguaje de Gemini para interpretar el texto extraído y clasificar los datos en productos, cantidades, precios y un total.

Almacenamiento en Google Sheets: Guarda los datos estructurados en una hoja de cálculo de Google, lo que permite un fácil acceso y análisis.

Arquitectura Modular: Diseñado con una arquitectura modular y una inyección de dependencias para mantener el código limpio, escalable y fácil de mantener.

💻 Estado del Proyecto
Actualmente, esta aplicación se encuentra en una etapa inicial (versión local), completamente funcional para pruebas en un entorno de desarrollo. Los siguientes pasos incluyen el despliegue a una plataforma de nube para su uso en producción.