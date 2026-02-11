describe('Generación de reporte', () => {
  it('genera el reporte cuando el análisis ha finalizado', () => {
    cy.visit('http://localhost:5173');

    cy.intercept('POST', '**/analizar').as('analizarRequest');

    cy.get('input[placeholder*="Ej:"]').type('Andrea Gonzalez');

    cy.get('input[type="date"]').first().type('2025-01-01');
    cy.get('input[type="date"]').last().type('2025-12-31');

    cy.contains('Iniciar Análisis').click();

    // 🔑 Esperar al backend (NO a la UI)
    cy.wait('@analizarRequest', { timeout: 120000 });

    // Ahora sí: la UI ya debería estar lista
    cy.contains(/Generar Reporte|Descargar Reporte/i, { timeout: 30000 })
      .should('be.visible')
      .click();
  });
});
