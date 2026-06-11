import sharp from 'sharp';

const cmd = process.argv[2];
const input = process.argv[3];

async function main() {
  switch (cmd) {
    case 'info': {
      const meta = await sharp(input).metadata();
      const stats = await sharp(input).stats();
      console.log(JSON.stringify({
        format: meta.format,
        width: meta.width,
        height: meta.height,
        space: meta.space,
        channels: meta.channels,
        depth: meta.depth,
        density: meta.density || null,
        hasAlpha: Boolean(meta.hasAlpha),
        pages: meta.pages || 1,
        size: meta.size || 0,
        stats: stats
      }, null, 2));
      break;
    }
    case 'resize': {
      const output = process.argv[4];
      const width = parseInt(process.argv[5] || '0');
      const height = parseInt(process.argv[6] || '0');
      const opts = {};
      if (width) opts.width = width;
      if (height) opts.height = height;
      if (!width && !height) {
        console.error('Specify at least width or height');
        process.exit(1);
      }
      await sharp(input).resize(opts).toFile(output);
      console.log(`Resized: ${input} -> ${output} (${width}x${height})`);
      break;
    }
    case 'convert': {
      const output = process.argv[4];
      const fmt = output.split('.').pop().toLowerCase();
      let pipeline = sharp(input);
      switch (fmt) {
        case 'jpg': case 'jpeg': pipeline = pipeline.jpeg(); break;
        case 'png': pipeline = pipeline.png(); break;
        case 'webp': pipeline = pipeline.webp(); break;
        case 'avif': pipeline = pipeline.avif(); break;
        case 'tiff': pipeline = pipeline.tiff(); break;
      }
      await pipeline.toFile(output);
      console.log(`Converted: ${input} -> ${output}`);
      break;
    }
    case 'rotate': {
      const output = process.argv[4];
      const degrees = parseInt(process.argv[5] || '90');
      await sharp(input).rotate(degrees).toFile(output);
      console.log(`Rotated: ${input} -> ${output} (${degrees}°)`);
      break;
    }
    case 'blur': {
      const output = process.argv[4];
      const sigma = parseFloat(process.argv[5] || '3');
      await sharp(input).blur(sigma).toFile(output);
      console.log(`Blurred: ${input} -> ${output} (sigma=${sigma})`);
      break;
    }
    case 'pipeline': {
      const output = process.argv[4];
      const width = parseInt(process.argv[5] || '0');
      const height = parseInt(process.argv[6] || '0');
      const quality = parseInt(process.argv[7] || '85');
      const fmt = output.split('.').pop().toLowerCase();
      let pipeline = sharp(input);
      if (width || height) pipeline = pipeline.resize({ width: width || undefined, height: height || undefined });
      switch (fmt) {
        case 'jpg': case 'jpeg': pipeline = pipeline.jpeg({ quality }); break;
        case 'png': pipeline = pipeline.png(); break;
        case 'webp': pipeline = pipeline.webp({ quality }); break;
        case 'avif': pipeline = pipeline.avif({ quality }); break;
      }
      await pipeline.toFile(output);
      console.log(`Pipeline: ${input} -> ${output} (${width||'auto'}x${height||'auto'}, q=${quality})`);
      break;
    }
    default:
      console.error('Unknown command');
      process.exit(1);
  }
}

main().catch(err => { console.error(err.message); process.exit(1); });
