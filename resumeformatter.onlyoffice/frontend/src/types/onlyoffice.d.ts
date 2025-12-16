// OnlyOffice Document Editor Type Definitions

interface Window {
  DocsAPI: {
    DocEditor: new (elementId: string, config: any) => {
      destroyEditor: () => void;
    };
  };
}
