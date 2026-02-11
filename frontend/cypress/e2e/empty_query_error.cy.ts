describe('Validación de búsqueda vacía', () => {
  it('no permite buscar sin ingresar un candidato', () => {
    cy.visit('http://localhost:5173');

    // Intentar enviar sin escribir query
    cy.contains('Iniciar Análisis').click();

    // El input es required → no debe enviarse
    cy.get('input[placeholder*="Ej:"]')
      .should('have.attr', 'required');
  });
});
