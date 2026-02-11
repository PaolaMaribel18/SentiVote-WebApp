describe('Filtro por rango de fechas', () => {
  it('permite aplicar un rango de fechas y obtener resultados', () => {
    cy.visit('http://localhost:5173');

    // Ingresar candidato
    cy.get('input[placeholder*="Ej:"]').type('Andrea Gonzalez');

    // Fecha inicio
    cy.get('input[type="date"]').first().type('2025-01-01');

    // Fecha fin
    cy.get('input[type="date"]').last().type('2025-12-31');

    // Ejecutar análisis
    cy.contains('Iniciar Análisis').click();

    // Verificar resultados
    cy.contains(/Resultados|Sentimiento|Análisis/i, { timeout: 10000 })
      .should('be.visible');
  });
});
