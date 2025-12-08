import { Search, Database, Brain, BarChart3, CheckCircle, ArrowRight } from 'lucide-react';

export function HowItWorksView() {
  const steps = [
    {
      number: '01',
      icon: <Search className="w-8 h-8" />,
      title: 'Ingresa tu Búsqueda',
      description: 'Escribe el nombre de un candidato, partido político o tema electoral que deseas analizar',
      details: [
        'Búsqueda flexible por nombre o tema',
        'Sugerencias automáticas',
        'Soporte para múltiples términos'
      ],
      color: 'from-blue-500 to-blue-600'
    },
    {
      number: '02',
      icon: <Database className="w-8 h-8" />,
      title: 'Recopilamos Datos',
      description: 'Nuestro sistema recopila millones de menciones de redes sociales, noticias y foros públicos',
      details: [
        'Análisis de redes sociales principales',
        'Monitoreo de medios digitales',
        'Verificación de fuentes confiables'
      ],
      color: 'from-purple-500 to-purple-600'
    },
    {
      number: '03',
      icon: <Brain className="w-8 h-8" />,
      title: 'Procesamiento Inteligente',
      description: 'Algoritmos de IA analizan el sentimiento, contexto y tendencias en los datos recopilados',
      details: [
        'Análisis de lenguaje natural',
        'Detección de contexto y sarcasmo',
        'Clasificación de sentimientos'
      ],
      color: 'from-pink-500 to-pink-600'
    },
    {
      number: '04',
      icon: <BarChart3 className="w-8 h-8" />,
      title: 'Visualización de Resultados',
      description: 'Recibe reportes detallados con gráficos interactivos y métricas clave',
      details: [
        'Dashboards interactivos',
        'Exportación de reportes',
        'Comparativas y tendencias'
      ],
      color: 'from-green-500 to-green-600'
    }
  ];

  const methodology = [
    {
      title: 'Recopilación de Datos',
      description: 'Agregamos datos de múltiples fuentes públicas verificadas'
    },
    {
      title: 'Limpieza y Filtrado',
      description: 'Eliminamos spam, bots y contenido duplicado'
    },
    {
      title: 'Análisis de Sentimiento',
      description: 'Clasificamos cada mención como positiva, neutral o negativa'
    },
    {
      title: 'Segmentación',
      description: 'Organizamos por demografía, geografía y temas'
    },
    {
      title: 'Visualización',
      description: 'Presentamos los resultados en formato fácil de entender'
    }
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-4">
            <h1 className="text-4xl font-bold text-gray-900">¿Cómo Funciona?</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Nuestra plataforma utiliza tecnología avanzada de inteligencia artificial para analizar millones de opiniones y generar insights precisos sobre el panorama electoral
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-12 mb-20">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="grid md:grid-cols-2 gap-8 items-center">
                {/* Content */}
                <div className={index % 2 === 1 ? 'md:order-2' : ''}>
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
                    <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl bg-gradient-to-br ${step.color} text-white mb-4`}>
                      {step.icon}
                    </div>
                    <div className="text-gray-400 mb-2">Paso {step.number}</div>
                    <h3 className="text-gray-900 mb-3">{step.title}</h3>
                    <p className="text-gray-600 mb-6">{step.description}</p>
                    <ul className="space-y-2">
                      {step.details.map((detail, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-gray-700">
                          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span>{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Visual */}
                <div className={index % 2 === 1 ? 'md:order-1' : ''}>
                  <div className={`bg-gradient-to-br ${step.color} rounded-2xl p-12 flex items-center justify-center min-h-[300px]`}>
                    <div className="text-center text-white">
                      <div className="text-6xl mb-4">{step.number}</div>
                      <div className="text-xl opacity-90">{step.title}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Arrow */}
              {index < steps.length - 1 && (
                <div className="flex justify-center my-8">
                  <ArrowRight className="w-8 h-8 text-gray-300 transform rotate-90" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Methodology */}
        <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12 border border-gray-200">
          <h2 className="text-gray-900 mb-8 text-center">Nuestra Metodología</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {methodology.map((item, index) => (
              <div key={index} className="relative">
                <div className="text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-full flex items-center justify-center mx-auto mb-4">
                    {index + 1}
                  </div>
                  <h4 className="text-gray-800 mb-2">{item.title}</h4>
                  <p className="text-gray-600">{item.description}</p>
                </div>
                {index < methodology.length - 1 && (
                  <div className="hidden md:block absolute top-6 left-full w-full h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 opacity-20 -z-10"></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Technology Stack */}
        <div className="mt-20">
          <h2 className="text-gray-900 mb-8 text-center">Tecnología que Utilizamos</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {['NLP Avanzado', 'Machine Learning', 'Big Data', 'Análisis Predictivo'].map((tech, index) => (
              <div key={index} className="bg-gradient-to-br from-gray-50 to-white p-6 rounded-xl border border-gray-200 text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg mx-auto mb-3"></div>
                <p className="text-gray-800">{tech}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
