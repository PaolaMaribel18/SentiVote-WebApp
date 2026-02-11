describe('Flujo principal de SentiVote', () => {
  it('permite buscar un candidato y mostrar resultados', () => {
    // 1. Abrir la app
    cy.visit('http://localhost:5173');

    // 2. Escribir el nombre del candidato
    cy.get('input[placeholder*="Ej:"]').type('Andrea Gonzalez');

    // 3. Enviar el formulario
    cy.contains('Iniciar Análisis').click();

    // 4. Verificar que aparecen resultados
    cy.contains(/Resultados|Análisis|Sentimiento/i, { timeout: 10000 })
      .should('be.visible');
  });
});
