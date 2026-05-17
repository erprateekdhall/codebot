import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import java from 'react-syntax-highlighter/dist/esm/languages/hljs/java';
import javascript from 'react-syntax-highlighter/dist/esm/languages/hljs/javascript';
import python from 'react-syntax-highlighter/dist/esm/languages/hljs/python';
import typescript from 'react-syntax-highlighter/dist/esm/languages/hljs/typescript';

// Register languages
SyntaxHighlighter.registerLanguage('java', java);
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('typescript', typescript);

interface CodeBlockProps {
  code: string;
  language?: string;
  fileName?: string;
  startLine?: number;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = 'java',
  fileName,
  startLine = 1,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg overflow-hidden border border-dark-300 my-2">
      {fileName && (
        <div className="bg-dark-800 text-dark-100 px-4 py-2 flex items-center justify-between text-sm">
          <span className="font-mono">{fileName}</span>
          <button
            onClick={handleCopy}
            className="text-dark-400 hover:text-white transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      )}
      <SyntaxHighlighter
        language={language}
        style={atomOneDark}
        showLineNumbers
        startingLineNumber={startLine}
        customStyle={{
          margin: 0,
          padding: '1rem',
          fontSize: '0.875rem',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
};
