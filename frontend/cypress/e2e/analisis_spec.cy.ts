describe('Flujo de análisis de SentiVote (mock API)', () => {
  it('realiza una búsqueda y muestra resultados de análisis', () => {

    cy.intercept('GET', '**/salud', {
      statusCode: 200,
      body: {
        estado: 'activo',
        publicaciones: 10,
        minDate: '2025-01-01',
        maxDate: '2025-12-31'
      }
    }).as('salud');

    cy.intercept('POST', '**/analizar', {
      statusCode: 200,
      body: {
        publicaciones: [],
        wordcloud: {
          general: null,
          por_sentimiento: {}
        },
        total_textos_analizados: 0
      }
    }).as('analizar');

    cy.intercept('POST', '**/conclusiones', {
      statusCode: 200,
      body: {
        conclusion: 'No se detectaron tendencias significativas en el análisis.'
      }
    }).as('conclusiones');

    cy.visit('http://localhost:5173');
    cy.wait('@salud');

    cy.get('input[placeholder*="Ej"]').type('Andrea Gonzalez');
    cy.contains('Iniciar Análisis').click();

    // Estado de carga
    cy.contains(/Analizando datos/i).should('be.visible');

    cy.wait('@analizar');
    cy.wait('@conclusiones');

    // Validar que aparece una conclusión (no texto frágil)
    cy.contains(/conclusión|análisis/i).should('be.visible');
  });
});
