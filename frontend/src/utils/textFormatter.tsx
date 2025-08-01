import React from 'react';

/**
 * Converts text with markdown-style formatting to JSX elements
 * Handles: **bold**, *italic*, `code`, and preserves line breaks
 */
export function formatMarkdownText(text: string): React.ReactNode {
  if (!text) return null;

  // Split text by line breaks first to preserve paragraph structure
  const paragraphs = text.split('\n\n');
  
  return paragraphs.map((paragraph, paragraphIndex) => {
    if (!paragraph.trim()) return null;

    const parts = [];
    let currentIndex = 0;
    
    // Pattern to match **bold**, *italic*, and `code`
    const markdownPattern = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)/g;
    let match;

    while ((match = markdownPattern.exec(paragraph)) !== null) {
      // Add text before the match
      if (match.index > currentIndex) {
        const beforeText = paragraph.slice(currentIndex, match.index);
        parts.push(beforeText);
      }

      // Add the formatted element
      if (match[2]) {
        // **bold**
        parts.push(<strong key={`bold-${paragraphIndex}-${match.index}`}>{match[2]}</strong>);
      } else if (match[3]) {
        // *italic*
        parts.push(<em key={`italic-${paragraphIndex}-${match.index}`}>{match[3]}</em>);
      } else if (match[4]) {
        // `code`
        parts.push(<code key={`code-${paragraphIndex}-${match.index}`}>{match[4]}</code>);
      }

      currentIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (currentIndex < paragraph.length) {
      parts.push(paragraph.slice(currentIndex));
    }

    // Handle line breaks within paragraphs
    const formattedParts = parts.map((part, partIndex) => {
      if (typeof part === 'string') {
        return part.split('\n').map((line, lineIndex, array) => (
          <React.Fragment key={`line-${paragraphIndex}-${partIndex}-${lineIndex}`}>
            {line}
            {lineIndex < array.length - 1 && <br />}
          </React.Fragment>
        ));
      }
      return part;
    }).flat();

    return (
      <p key={`paragraph-${paragraphIndex}`}>
        {formattedParts}
      </p>
    );
  }).filter(Boolean);
}

/**
 * Simple text formatter that just handles basic markdown without paragraphs
 */
export function formatInlineMarkdown(text: string): React.ReactNode {
  if (!text) return null;

  const parts = [];
  let currentIndex = 0;
  
  const markdownPattern = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)/g;
  let match;

  while ((match = markdownPattern.exec(text)) !== null) {
    // Add text before the match
    if (match.index > currentIndex) {
      const beforeText = text.slice(currentIndex, match.index);
      parts.push(beforeText);
    }

    // Add the formatted element
    if (match[2]) {
      // **bold**
      parts.push(<strong key={`bold-${match.index}`}>{match[2]}</strong>);
    } else if (match[3]) {
      // *italic*
      parts.push(<em key={`italic-${match.index}`}>{match[3]}</em>);
    } else if (match[4]) {
      // `code`
      parts.push(<code key={`code-${match.index}`}>{match[4]}</code>);
    }

    currentIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (currentIndex < text.length) {
    parts.push(text.slice(currentIndex));
  }

  return parts.length > 0 ? parts : text;
}
