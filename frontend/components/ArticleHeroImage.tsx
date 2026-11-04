"use client";

import React, { useState } from "react";

interface ArticleHeroImageProps {
  src?: string;
  alt: string;
}

export default function ArticleHeroImage({ src, alt }: ArticleHeroImageProps) {
  const [imgSrc, setImgSrc] = useState(src || "/images/news-default.svg");

  const handleError = () => {
    if (imgSrc !== "/images/news-default.svg") {
      setImgSrc("/images/news-default.svg");
    }
  };

  return (
    <img
      src={imgSrc}
      alt={alt}
      onError={handleError}
      className="w-full h-full object-cover transition-opacity duration-300"
    />
  );
}
