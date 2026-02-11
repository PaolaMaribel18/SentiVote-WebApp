// cypress/integration/end_to_end_spec.js

describe('Caso de uso completo: búsqueda, visualización y descarga de informe', () => {
  beforeEach(() => {
    // intercepta el endpoint /salud
    cy.intercept('GET', '**/salud', {
      statusCode: 200,
      body: {
        estado: 'activo', publicaciones: 50,
        minDate: '2025-01-01', maxDate: '2025-12-31'
      }
    });
    // intercepta el endpoint /analizar con resultados simulados
    cy.intercept('POST', '**/analizar', {
      statusCode: 200,
      body: {
        publicaciones: [
          {
            id_post: '1', texto: 'Buen trabajo del candidato', usuario: 'user1', candidato: 'Noboa', fecha: '2025-05-10',
            sentiment: 'POS', confidence: 0.9, comments: [], sentimiento_final: 'POS'
          },
        ],
        wordcloud: {
          general: null,
          por_sentimiento: {}
        },
        total_textos_analizados: 1
      }
    });
  });

  it('permite al usuario buscar un candidato y descargar un informe', () => {
    cy.visit('http://localhost:5173');
    cy.get('input[placeholder*="Ej"]').type('Noboa');
    cy.contains('Iniciar Análisis').click();
    // espera que se muestre la tarjeta de sentimiento positivo
    cy.contains('Positivo');
    cy.contains('publicaciones', { matchCase: false });
    
    // suponer que hay un botón o enlace para generar PDF
    cy.contains('Generar PDF').click();
    // verificar que se haya iniciado la descarga (Cypress puede validar cabeceras de respuesta)
  });
});
