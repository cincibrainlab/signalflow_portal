export const preloadComponents = () => {
  return `
    <link rel="modulepreload" href="/src/lib/components/ui/table/index.ts" />
    <link rel="modulepreload" href="/src/lib/components/ui/card/index.ts" />
    <link rel="modulepreload" href="/src/lib/components/ui/button/index.ts" />
    <link rel="modulepreload" href="/src/lib/components/ui/input/index.ts" />
    <link rel="modulepreload" href="/src/lib/components/ui/badge/index.ts" />
    <link rel="modulepreload" href="/src/lib/components/ui/select/index.ts" />
  `;
};
