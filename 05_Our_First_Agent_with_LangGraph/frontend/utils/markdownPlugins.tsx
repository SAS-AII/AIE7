import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import remarkEmoji from 'remark-emoji';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import { PluggableList } from 'unified';

// Pre-configured remark plugins
export const remarkPlugins: PluggableList = [
  remarkGfm, // GitHub Flavored Markdown (tables, strikethrough, etc.)
  remarkMath, // Math expressions
  remarkBreaks, // Line breaks
  remarkEmoji, // Emoji support
];

// Pre-configured rehype plugins
export const rehypePlugins: PluggableList = [
  rehypeKatex, // Math rendering
  [rehypeHighlight, { detect: true, ignoreMissing: true }], // Syntax highlighting
];

// Custom components for ReactMarkdown
export const markdownComponents = {
  // Custom code block component
  code: ({ node, inline, className, children, ...props }: any) => {
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : '';
    
    if (inline) {
      return (
        <code 
          className="bg-gray-100 dark:bg-gray-800 rounded px-1 py-0.5 text-sm font-mono text-chess-accent"
          {...props}
        >
          {children}
        </code>
      );
    }
    
    return (
      <div className="relative">
        {language && (
          <div className="absolute top-0 right-0 bg-gray-200 dark:bg-gray-700 text-xs px-2 py-1 rounded-bl text-gray-600 dark:text-gray-300">
            {language}
          </div>
        )}
        <code 
          className={`${className} block bg-gray-100 dark:bg-gray-800 rounded-lg p-4 overflow-x-auto text-sm font-mono`}
          {...props}
        >
          {children}
        </code>
      </div>
    );
  },
  
  // Custom blockquote component
  blockquote: ({ children, ...props }: any) => (
    <blockquote 
      className="border-l-4 border-chess-accent bg-chess-light/20 dark:bg-chess-dark/20 pl-4 py-2 my-4 italic"
      {...props}
    >
      {children}
    </blockquote>
  ),
  
  // Custom table components
  table: ({ children, ...props }: any) => (
    <div className="overflow-x-auto my-4">
      <table 
        className="min-w-full border-collapse border border-gray-300 dark:border-gray-600"
        {...props}
      >
        {children}
      </table>
    </div>
  ),
  
  th: ({ children, ...props }: any) => (
    <th 
      className="border border-gray-300 dark:border-gray-600 bg-chess-light/50 dark:bg-chess-dark/50 px-4 py-2 text-left font-semibold"
      {...props}
    >
      {children}
    </th>
  ),
  
  td: ({ children, ...props }: any) => (
    <td 
      className="border border-gray-300 dark:border-gray-600 px-4 py-2"
      {...props}
    >
      {children}
    </td>
  ),
  
  // Custom link component
  a: ({ href, children, ...props }: any) => (
    <a 
      href={href}
      className="text-chess-accent hover:underline focus:underline focus:outline-none"
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    >
      {children}
    </a>
  ),
  
  // Custom heading components
  h1: ({ children, ...props }: any) => (
    <h1 
      className="text-2xl font-bold mb-4 mt-6 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2"
      {...props}
    >
      {children}
    </h1>
  ),
  
  h2: ({ children, ...props }: any) => (
    <h2 
      className="text-xl font-semibold mb-3 mt-5 text-gray-900 dark:text-white"
      {...props}
    >
      {children}
    </h2>
  ),
  
  h3: ({ children, ...props }: any) => (
    <h3 
      className="text-lg font-medium mb-2 mt-4 text-gray-900 dark:text-white"
      {...props}
    >
      {children}
    </h3>
  ),
  
  // Custom paragraph component
  p: ({ children, ...props }: any) => (
    <p className="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed" {...props}>
      {children}
    </p>
  ),
  
  // Custom list components
  ul: ({ children, ...props }: any) => (
    <ul className="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300" {...props}>
      {children}
    </ul>
  ),
  
  ol: ({ children, ...props }: any) => (
    <ol className="list-decimal list-inside mb-4 text-gray-700 dark:text-gray-300" {...props}>
      {children}
    </ol>
  ),
  
  li: ({ children, ...props }: any) => (
    <li className="mb-1" {...props}>
      {children}
    </li>
  ),
  
  // Custom horizontal rule
  hr: ({ ...props }: any) => (
    <hr className="my-6 border-gray-300 dark:border-gray-600" {...props} />
  ),
  
  // Custom strong/bold component
  strong: ({ children, ...props }: any) => (
    <strong className="font-semibold text-gray-900 dark:text-white" {...props}>
      {children}
    </strong>
  ),
  
  // Custom emphasis/italic component
  em: ({ children, ...props }: any) => (
    <em className="italic text-gray-700 dark:text-gray-300" {...props}>
      {children}
    </em>
  ),
};

// Default markdown configuration
export const defaultMarkdownConfig = {
  remarkPlugins,
  rehypePlugins,
  components: markdownComponents,
  skipHtml: true, // Skip HTML for security
  // linkTarget removed, handled by custom link renderer
  transformImageUri: (uri: string) => uri, // Pass through image URIs
}; 