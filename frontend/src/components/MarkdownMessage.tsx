import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownMessageProps {
  content: string;
}

/**
 * Markdown 訊息渲染組件
 * 支援標題、粗體、斜體、刪除線、引用、列表等格式
 */
export const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // 標題樣式
        h1: ({ children }) => (
          <h1 className="text-xl font-bold mb-2 mt-3 first:mt-0">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-base font-bold mb-1.5 mt-2.5 first:mt-0">{children}</h3>
        ),
        h4: ({ children }) => (
          <h4 className="text-sm font-bold mb-1.5 mt-2 first:mt-0">{children}</h4>
        ),
        h5: ({ children }) => (
          <h5 className="text-sm font-semibold mb-1 mt-2 first:mt-0">{children}</h5>
        ),
        h6: ({ children }) => (
          <h6 className="text-xs font-semibold mb-1 mt-2 first:mt-0">{children}</h6>
        ),

        // 段落樣式
        p: ({ children }) => (
          <p className="mb-2 last:mb-0 whitespace-pre-wrap">{children}</p>
        ),

        // 無序列表
        ul: ({ children }) => (
          <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
        ),

        // 有序列表
        ol: ({ children }) => (
          <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
        ),

        // 列表項目
        li: ({ children }) => (
          <li className="ml-2">{children}</li>
        ),

        // 引用區塊
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-gray-300 pl-3 py-1 my-2 italic text-gray-700">
            {children}
          </blockquote>
        ),

        // 行內程式碼
        code: ({ children, className }) => {
          // 如果有 className，表示是程式碼區塊（已被 pre 包裹）
          if (className) {
            return <code className={className}>{children}</code>;
          }
          // 行內程式碼
          return (
            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">
              {children}
            </code>
          );
        },

        // 程式碼區塊
        pre: ({ children }) => (
          <pre className="bg-gray-100 p-3 rounded my-2 overflow-x-auto">
            {children}
          </pre>
        ),

        // 粗體
        strong: ({ children }) => (
          <strong className="font-bold">{children}</strong>
        ),

        // 斜體
        em: ({ children }) => (
          <em className="italic">{children}</em>
        ),

        // 刪除線
        del: ({ children }) => (
          <del className="line-through opacity-75">{children}</del>
        ),

        // 連結
        a: ({ children, href }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            {children}
          </a>
        ),

        // 水平分隔線
        hr: () => <hr className="my-3 border-gray-300" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownMessage;
