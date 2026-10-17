import Image from "next/image";

// Every image is labelled, so an illustration is never mistaken for a news photo.
export function StoryImage({
  src,
  alt,
  sizes,
  eager = false,
  className = "",
}: {
  src: string;
  alt: string;
  sizes: string;
  eager?: boolean;
  className?: string;
}) {
  return (
    <div className={`relative aspect-[3/2] overflow-hidden rounded-lg bg-soft ${className}`}>
      <Image
        src={src}
        alt={alt}
        fill
        sizes={sizes}
        loading={eager ? "eager" : "lazy"}
        fetchPriority={eager ? "high" : undefined}
        className="object-cover"
      />
      <span className="absolute bottom-2 left-2 rounded bg-ink/80 px-2 py-0.5 text-[11px] font-medium text-white">
        AI illustration
      </span>
    </div>
  );
}
