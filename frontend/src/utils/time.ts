function convertTimeToSeconds(time: string) {
  const [minutes, seconds] = time.split(":").map(Number);
  return minutes * 60 + seconds;
}

export function extractCulturalLexicons(schema: any) {
  const lexicons: any = [];
  schema.forEach((entry: any) => {
    const startSeconds = convertTimeToSeconds(entry.startTime);
    const endSeconds = convertTimeToSeconds(entry.endTime);
    entry.culturalLexicon.forEach((lexicon: any) => {
      const lexiconEntry = {
        start: startSeconds,
        end: endSeconds,
        term: lexicon.term,
        explanation: lexicon.explanation,
      };
      lexicons.push(lexiconEntry);
    });
  });
  console.log("Lexicons:\n\n", lexicons);
  return lexicons;
}

function convertTimeForVTT(time: string) {
  const [minutes, seconds] = time.split(":").map(Number);
  return `00:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
    2,
    "0"
  )}.000`;
}

// export function createVttFile(subtitles: any) {
//   let vttContent = "WEBVTT\n\n";
//   subtitles.forEach((subtitle: any) => {
//     const startTime = convertTimeForVTT(subtitle.startTime);
//     const endTime = convertTimeForVTT(subtitle.endTime);
//     const text = subtitle.Subtitle;
//     vttContent += `${startTime} --> ${endTime}\n${text}\n\n`;
//   });
//   fs.writeFile("/frontend/public/subtitles.vtt", vttContent, "utf-8");
//   console.log("VTT file created");
// }
