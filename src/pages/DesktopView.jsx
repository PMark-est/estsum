import React, { useEffect, useState } from "react";
import {
  Button,
  Input,
  InputAdornment,
  Typography,
  CircularProgress,
} from "@mui/material";
import Slider from "@mui/material/Slider";
import SendIcon from "@mui/icons-material/Send";
import UTLogo from "../assets/ut.svg";
import NLPLogo from "../assets/nlp.svg";

const DesktopView = () => {
  const [constants, setConstants] = useState({
    summaryLength: 30,
    alpha: 0.4,
    beta: 0.4,
    gamma: 0.2,
  });
  const [inputValue, setInputValue] = useState("");
  const [summary, setSummary] = useState({ title: "", summary: [] });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setIsLoading(true);
    const response = await fetch("http://localhost:8080/api/summarize/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ...constants, url: inputValue }),
    });

    const json = await response.json();

    setSummary({ summary: json.summary, title: json.title });
    setIsLoading(false);
  };

  return (
    <>
      <header className="w-full pl-8 h-[133px] bg-[#2C5696]">
        <img
          src={UTLogo}
          className="pt-[10px] pb-1"
          alt="UT"
          width={276}
          height={50}
        />
        <img
          src={NLPLogo}
          className="pt-[20px]"
          alt="NLP"
          width={160}
          height={20}
        />
      </header>
      <main className="flex flex-1">
        <aside className="flex flex-col gap-24 mt-34 ml-8 w-1/5">
          <span>
            <h2 className="pb-10">
              Kokkuvõtte pikkus (nt 30% tähendab, et kokkuvõte on 30% artikli
              kogupikkusest)
            </h2>
            <Slider
              track={false}
              valueLabelDisplay="on"
              value={constants.summaryLength}
              onChange={(e, val) =>
                setConstants((prev) => ({ ...prev, summaryLength: val }))
              }
            />
          </span>
          <div>
            <h2 className="text-center text-3xl mb-14">Arendajatele</h2>
            <span className="flex gap-6">
              <h2 className="pb-10">{"\u03B1"}</h2>
              <Slider
                track={false}
                valueLabelDisplay="on"
                max={1}
                value={constants.alpha}
                onChange={(e, val) =>
                  setConstants((prev) => ({ ...prev, alpha: val }))
                }
                step={0.01}
              />
            </span>
            <span className="flex gap-6">
              <h2 className="pb-10">{"\u03B2"}</h2>
              <Slider
                track={false}
                valueLabelDisplay="on"
                max={1}
                value={constants.beta}
                onChange={(e, val) =>
                  setConstants((prev) => ({ ...prev, beta: val }))
                }
                step={0.01}
              />
            </span>
            <span className="flex gap-6">
              <h2 className="pb-10">{"\u03B3"}</h2>
              <Slider
                track={false}
                valueLabelDisplay="on"
                max={1}
                value={constants.gamma}
                onChange={(e, val) =>
                  setConstants((prev) => ({ ...prev, gamma: val }))
                }
                step={0.01}
              />
            </span>
          </div>
        </aside>
        <div className="flex flex-col flex-1 mt-12 items-center">
          <h1 className="mb-4">Kokkuvõte</h1>
          <div className="w-[600px] min-h-[200px] max-h-[550px] mb-12 border-1 overflow-y-auto rounded-md">
            {isLoading ? (
              <div className="flex justify-center mt-12">
                <CircularProgress size={24} color="inherit" />
              </div>
            ) : (
              <>
                <h1 className="text-center">{summary.title}</h1>
                {summary.summary.map((sentence, index) => (
                  <Typography key={index} sx={{ mb: 2 }}>
                    {sentence}
                  </Typography>
                ))}
              </>
            )}
          </div>
          <form className="flex w-full" onSubmit={handleSubmit}>
            <Input
              disableUnderline
              onChange={(e) => setInputValue(e.target.value)}
              value={inputValue}
              sx={{
                border: "1px solid #000",
                borderRadius: "8px",
                margin: "auto",
                width: "50%",
              }}
              placeholder="Sisesta veebiaadress"
              endAdornment={
                <InputAdornment position="end">
                  <Button type="submit">
                    <SendIcon />
                  </Button>
                </InputAdornment>
              }
            />
          </form>
        </div>
        <aside className="w-1/5"></aside>
      </main>
    </>
  );
};

export default DesktopView;
