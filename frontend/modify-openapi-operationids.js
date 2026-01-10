import fs from 'fs';
import path from 'path';

const openApiPath = path.join(process.cwd(), 'openapi.json');

// Read the OpenAPI schema
const openApiSchema = JSON.parse(fs.readFileSync(openApiPath, 'utf8'));

// Modify operationIds to be camelCase
function modifyOperationIds(schema) {
    if (!schema.paths) return schema;

    Object.keys(schema.paths).forEach(path => {
        const pathItem = schema.paths[path];
        Object.keys(pathItem).forEach(method => {
            if (['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {
                const operation = pathItem[method];
                if (operation && !operation.operationId) {
                    // Generate operationId from path and method
                    const pathParts = path.split('/').filter(Boolean);
                    const operationName = pathParts
                        .map((part, index) => {
                            if (index === 0) {
                                return part;
                            }
                            return part.charAt(0).toUpperCase() + part.slice(1);
                        })
                        .join('');
                    operation.operationId = `${method.toLowerCase()}${operationName.charAt(0).toUpperCase() + operationName.slice(1)}`;
                }
            }
        });
    });

    return schema;
}

// Modify the schema
const modifiedSchema = modifyOperationIds(openApiSchema);

// Write back to file
fs.writeFileSync(openApiPath, JSON.stringify(modifiedSchema, null, 2), 'utf8');

console.log('OpenAPI schema modified successfully!');
