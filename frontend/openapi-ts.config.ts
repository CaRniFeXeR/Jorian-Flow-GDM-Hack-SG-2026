import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: '@hey-api/client-axios',
  input: './openapi.json',
  output: {
    path: './src/client',
    format: 'prettier',
  },
  types: {
    enums: 'javascript',
  },
});
