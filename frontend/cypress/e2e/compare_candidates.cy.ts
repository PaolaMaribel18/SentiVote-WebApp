// frontend/cypress/e2e/compare_candidates.cy.ts

describe('Comparación de candidatos', () => {
  it('compara dos candidatos cuando ambos análisis finalizan', () => {

    cy.visit('http://localhost:5173');

    // 👉 Navegar a la vista Comparar (NAVBAR)
    cy.get('nav').contains('Comparar').click();

    // 👉 Interceptar llamadas al backend
    cy.intercept('POST', '**/analizar').as('analizarRequest');

    // 👉 Seleccionar candidatos
    cy.get('select').eq(0).select('Andrea Gonzalez Nader');
    cy.get('select').eq(1).select('Daniel Noboa');

    // 👉 Click en el botón del formulario (no el navbar)
    cy.get('button')
      .filter(':contains("Comparar")')
      .last()
      .click();

    // 👉 Esperar las DOS ejecuciones del backend
    cy.wait('@analizarRequest', { timeout: 240000 });
    cy.wait('@analizarRequest', { timeout: 240000 });

    // 👉 Validación funcional (datos renderizados)
    cy.contains('Andrea Gonzalez', { timeout: 30000 })
      .should('be.visible');

    cy.contains('Daniel Noboa')
      .should('be.visible');
  });
});
