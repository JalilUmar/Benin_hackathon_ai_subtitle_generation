"use client";

import { extractCulturalLexicons } from "@/utils/time";
import React, { useState, useRef, useEffect } from "react";
import Title from "./title";
import toast, { Toaster } from "react-hot-toast";
import { completionToast, errorToast, successToast } from "@/utils/toaster";
import Image from "next/image";

const VideoFilePlayer: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [language, setlanguage] = useState<string>("");
  const videoRef = useRef<HTMLVideoElement>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [lexicons, setLexicons] = useState<any[]>([]);
  const [showSubtitles, setShowSubtitles] = useState<boolean>(false);
  const [showImages, setShowImages] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const [currentTime, setCurrentTime] = useState(0);
  const [visibleLexicons, setVisibleLexicons] = useState<any[]>([]);

  const languageOptions: string[] = [
    "English",
    "Spanish",
    "French",
    "German",
    "Chinese",
    "Japanese",
    "Korean",
    "Portuguese",
    "Russian",
    "Arabic",
    "Italian",
    "Dutch",
    "Polish",
    "Romanian",
    "Swedish",
    "Turkish",
    "Vietnamese",
  ];

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
        if (data.json_res) {
          setLexicons(extractCulturalLexicons(data.json_res));
          setShowSubtitles(true);
          successToast("Subtitles Generated Successfully!");
          setLoading(false);
        } else if (data.message) {
          setShowImages(true);
          console.log(data.message);
        } else {
          console.log("Data not arrived yet");
        }
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
    <div className="mt-[100px]">
      {!videoFile && (
        <div className="flex  items-center justify-center ">
          <label
            htmlFor="dropzone-file"
            className="flex flex-col items-center justify-center w-full h-screen border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
          >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <svg
                aria-hidden="true"
                className="w-10 h-10 mb-3 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.904 6a4 4 0 01-7.902.88l-.82.82a2 2 0 11-2.828-2.828l.82.82A3 3 0 0313 12a3 3 0 00-7 2.828l.82.82a2 2 0 11-2.828-2.828l-.82-.82z"
                ></path>
              </svg>
              <p className="mb-2 text-sm text-gray-500">
                <span className="font-semibold">
                  Click to upload your favorite music
                </span>{" "}
                or drag and drop
              </p>
              <p className="text-xs text-gray-500">
                MP4, MOV, AVI, MKV up to 10MB
              </p>
            </div>
            <input
              id="dropzone-file"
              type="file"
              className="hidden"
              onChange={handleVideoUpload}
              accept=".mp4,.mov,.avi,.mkv"
            />
          </label>
        </div>
      )}

      <div className="flex justify-center items-center gap-x-[20px]">
        {showImages && (
          <div className="w-1/4 text-2xl font-bold font-sans text-center grid gap-y-5 justify-center ">
            <h3>Related Images</h3>

            <Image
              src={"/1.jpeg"}
              alt=""
              height="200"
              width="200"
              className="rounded-md"
            />
            <Image
              src={"/2.jpeg"}
              alt=""
              height="200"
              width="200"
              className="rounded-md"
            />
            <Image
              src={"/3.jpeg"}
              alt=""
              height="200"
              width="200"
              className="rounded-md"
            />
          </div>
        )}
        {videoFile && (
          <div className="grid justify-center items-center w-2/4">
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
              className="border border-gray-300 rounded px-4 py-2 mb-4 text-black overflow-x-auto"
              value={language}
              onChange={(e) => setlanguage(e.target.value)}
              disabled={loading}
            >
              <option value="null">Please select a language</option>
              {languageOptions.map((lang: string) => {
                return (
                  <option value={lang} key={lang}>
                    {lang}
                  </option>
                );
              })}
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

        <div className="grid justify-center w-1/4 ">
          {visibleLexicons.length > 0 && (
            <h3 className="text-2xl font-bold font-sans text-center">
              Cultural Words
            </h3>
          )}
          {visibleLexicons.map((item: any) => (
            <div
              key={item.term}
              className="max-w-[300px] rounded overflow-hidden shadow-lg bg-white m-4 p-6"
            >
              <div className="font-bold text-xl mb-2 text-indigo-500">
                {item.term}
              </div>
              <p className="text-gray-700 text-base">{item.explanation}</p>
            </div>
          ))}
        </div>
      </div>
      <Toaster />
    </div>
  );
};

export default VideoFilePlayer;
