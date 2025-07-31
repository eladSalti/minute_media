export default [
  {
    files: ['**/*.js', '**/*.ts'],
    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 'latest'
    },
    rules: {
      semi: 'error',
      quotes: ['error', 'single']
    }
  }
];
