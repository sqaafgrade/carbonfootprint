/**
 * Skip link for keyboard navigation — allows users to bypass
 * repetitive navigation and jump directly to main content.
 *
 * WCAG 2.1 SC 2.4.1 (Level A)
 */

import React from 'react';

interface SkipLinkProps {
  targetId?: string;
  label?: string;
}

export const SkipLink: React.FC<SkipLinkProps> = ({
  targetId = 'main-content',
  label = 'Skip to main content',
}) => {
  return (
    <a
      href={`#${targetId}`}
      className="skip-link"
      id="skip-link"
    >
      {label}
    </a>
  );
};
