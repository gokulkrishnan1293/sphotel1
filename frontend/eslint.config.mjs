import tseslint from 'typescript-eslint'
import boundaries from 'eslint-plugin-boundaries'

export default tseslint.config(
  ...tseslint.configs.strict,
  {
    plugins: { boundaries },
    settings: {
      'boundaries/elements': [
        { type: 'feature', pattern: 'src/features/*', capture: ['name'] },
        { type: 'shared', pattern: 'src/shared/*' },
        { type: 'lib', pattern: 'src/lib/*' },
        { type: 'app', pattern: 'src/app/*' },
      ],
    },
    rules: {
      // No any type — ever
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

      // Cross-feature import barrier:
      // billing/ cannot import from kitchen-display/ — must go through shared/
      'boundaries/element-types': ['error', {
        default: 'disallow',
        rules: [
          // Feature may import from itself, shared, lib — never from other features
          { from: 'feature', allow: [['feature', { name: '${from.name}' }], 'shared', 'lib'] },
          { from: 'shared', allow: ['shared', 'lib'] },
          { from: 'lib', allow: ['lib'] },
          { from: 'app', allow: ['feature', 'shared', 'lib'] },
        ],
      }],
    },
  }
)
