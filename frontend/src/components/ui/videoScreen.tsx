"use client";

import { extractCulturalLexicons } from "@/utils/time";
import React, { useState, useRef, useEffect } from "react";
import Title from "./title";
import toast, { Toaster } from "react-hot-toast";
import { completionToast, errorToast, successToast } from "@/utils/toaster";

const VideoFilePlayer: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [language, setlanguage] = useState<string>("");
  const videoRef = useRef<HTMLVideoElement>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [lexicons, setLexicons] = useState<any[]>([]);
  const [showSubtitles, setShowSubtitles] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const [currentTime, setCurrentTime] = useState(0);
  const [visibleLexicons, setVisibleLexicons] = useState<any[]>([]);

  useEffect(() => {
    if (videoFile) {
      const socket = new WebSocket("ws://localhost:8000/subtitle/ws");
      setWs(socket);

      socket.onopen = () => {
        console.log("WebSocket connected");
        sendVideo();
      };

      socket.onmessage = (event) => {
        // setWsData(event.data);
        const data = JSON.parse(event.data); // Parse incoming JSON data
        console.log(data);
        setLexicons(extractCulturalLexicons(data));
        setShowSubtitles(true);
        successToast("Subtitles Generated Successfully!");
        setLoading(false);
      };

      socket.onclose = () => {
        console.log("WebSocket closed");
      };

      socket.onerror = (error) => {
        console.log("Ooops! something went wrong\n", error);
        errorToast("Ooops! Something went wrong.");
      };

      return () => {
        socket.close();
      };
    }
  }, [videoFile]);

  const handleVideoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setVideoFile(file);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const newCurrentTime = videoRef.current.currentTime;
      setCurrentTime(newCurrentTime);

      // Filter lexicons based on current time
      const newVisibleLexicons = lexicons.filter(
        (lexicon) =>
          lexicon.start <= newCurrentTime && newCurrentTime <= lexicon.end
      );

      setVisibleLexicons(newVisibleLexicons);
    }
  };
  const sendVideo = () => {
    if (ws && videoFile) {
      setLoading(true);
      successToast("Generating Subtitles Please Wait...");
      const chunkSize = 1024 * 1024; // 1MB chunks
      let offset = 0;
      const reader = new FileReader();

      reader.onload = () => {
        const chunk = reader.result as ArrayBuffer;

        // Determine isLastChunk BEFORE incrementing offset
        const isLastChunk = offset + chunkSize >= videoFile.size;

        const payload = JSON.stringify({
          lang: language,
          videoChunk: Array.from(new Uint8Array(chunk)),
          isLastChunk: isLastChunk, // Use the corrected value
        });
        ws.send(payload);
        console.log("Chunk sent", offset, videoFile.size, isLastChunk);
        offset += chunkSize;

        if (offset < videoFile.size) {
          readNextChunk();
        }
      };

      const readNextChunk = () => {
        const slice = videoFile.slice(offset, offset + chunkSize);
        reader.readAsArrayBuffer(slice);
      };

      readNextChunk(); // Start reading the first chunk
    }
  };

  return (
    <div className="mt-4">
      {!videoFile && (
        <div className="grid justify-center items-center">
          <Title />
          <input
            type="file"
            accept=".mp4,.mov,.avi,.mkv"
            onChange={handleVideoUpload}
            className="border border-gray-300 rounded px-4 py-2 mb-4"
          />
        </div>
      )}

      {videoFile && (
        <div className="grid justify-center items-center">
          <video
            className="w-full rounded-lg shadow-lg mb-4"
            controls
            ref={videoRef}
            onTimeUpdate={handleTimeUpdate}
          >
            <source src={URL.createObjectURL(videoFile)} type="video/mp4" />
            {showSubtitles && (
              <track
                src="/subtitle.vtt"
                kind="subtitles"
                label="Subtitles"
                default
              />
            )}
            Your browser does not support the video tag.
          </video>

          <label className="block mb-2 text-lg font-semibold">
            Select a language for subtitles:
          </label>
          <select
            className="border border-gray-300 rounded px-4 py-2 mb-4 text-black"
            value={language}
            onChange={(e) => setlanguage(e.target.value)}
            defaultValue={"English"}
            disabled={loading}
          >
            <option value="English">English</option>
            <option value="French">French</option>
            <option value="Spanish">Spanish</option>
            <option value="German">German</option>
            <option value="Chinese">Chinese</option>
            <option value="Hindi">Hindi</option>
          </select>

          <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg"
            onClick={sendVideo}
            disabled={loading}
          >
            {loading ? "Generating subtitles ..." : "Generate Subtitles"}
          </button>
        </div>
      )}

      {/* {visibleLexicons.map((item: any) => {
        return (
          <div className="Grid justify-center items-center" key={item.term}>
            <span>
              <h3>Term:</h3>
              <p>{item.term}</p>
            </span>
            <span>
              <h3>Meaning:</h3>
              <p>{item.explanation}</p>
            </span>
          </div>
        );
      })} */}
      <div className="grid justify-center items-center">
        {visibleLexicons.map((item: any) => (
          <div
            key={item.term}
            className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-4 p-6"
          >
            <div className="font-bold text-xl mb-2 text-indigo-500">
              {item.term}
            </div>
            <p className="text-gray-700 text-base">{item.explanation}</p>
          </div>
        ))}
      </div>
      <Toaster />
    </div>
  );
};

export default VideoFilePlayer;
