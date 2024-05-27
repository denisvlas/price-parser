
import { useEffect, useState } from "react";
import styles from "./App.module.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import axios from "axios";
import { data } from "../utils/models";
import ProductsSection from "./ProductsSection";
import socketIOClient from "socket.io-client";
import ProgressBar from "./ProgressBar";

function App() {
  // i neet the input to send a request to the server

  const [search, setSearch] = useState("");
  const [data, setData] = useState<data[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  useEffect((): any => {
    const socket = socketIOClient("http://103.241.66.38:5000");
    socket.on("progress", (data) => {
      setProgress(data.progress);
      // Afișează progresul sau poți face orice alte actualizări în interfața utilizatorului
    });

    return () => socket.disconnect(); // Deconectează socketul când componenta se demontează sau se actualizează
  }, []);

  const handleSearch = (e: any) => {
    setSearch(e.target.value);
  };

  const searchProducts = async () => {
    setProgress(0);
    setLoading(true);

    try {
      const response = await axios.post("http://103.241.66.38:5000/parse_all", {
        search,
      });
      setData(response.data);
      console.log(response.data)
      if(response.data.length>0){
        setTimeout(() => {
        setLoading(false);
          
        }, 1200);
      }
      setCurrentPage(1);
      setPages(response.data.length/8);
      console.log(Math.round(response.data.length/8));
      
    } catch (err) {
      console.log(err);
    }
    // setSearch('');
  };

  useEffect(() => {
    console.log(data);
  }, [data]);

  const choices = ["Scumpe", "Ieftine", "Reduceri"];
  const [filter, setFilter] = useState("Scumpe");
  const [pages, setPages] = useState(0);


  useEffect(() => {
    filterProjects();
    console.log(filter);
  }, [filter]);

  async function filterProjects() {
    
    try {
      const res = await axios.post("http://103.241.66.38:5000/filter", {
        data: data,
        filter: filter,
      });
      console.log(res.data);
      setData(res.data);
      setCurrentPage(1);
      console.log(res.data);
    } catch (e) {
      console.log(e);
    }
  }

  function handleChangeFilter(value: string) {
    setFilter(value);
  }

  const handleKeyPress = (e: any) => {
    if (e.key === "Enter") {
      searchProducts();
    }
  };

  const [currentPage, setCurrentPage] = useState(1);


  
  return (
    <div className={styles.container}>
      
      {data.length==0&&<h1 style={{ fontSize: 25,marginTop:50 }}>BESTPRICE.STORE</h1>}
      
      <div className={styles.nav}>
      {loading&&<ProgressBar progress={progress} />}

      <section className={styles["filtru-section"]}>
          <select
            onChange={(e) => handleChangeFilter(e.target.value)}
            className={styles.filtru}
          >
            {choices.map((c, index) => {
              return (
                <option value={c} key={index}>
                  {c}
                </option>
              );
            })}
          </select>
        </section>
        
        <div className={styles["input-container"]}>
          <input
            onKeyPress={handleKeyPress}
            onChange={handleSearch}
            value={search}
            type="text"
            placeholder="Caută produse"
          />
          <i
            onClick={searchProducts}
            className={`bi bi-search ${styles["search-icon"]}`}
          ></i>
        </div>
        
      </div>
  <div style={{textAlign:"center"}}>
      {Array.from({length: pages}, (_, i) => i + 1).map((p, index) => {
        return (
          <a style={{marginLeft:20,fontSize:`${currentPage===p?'25px':'20px'}`, cursor:"pointer"}} onClick={() => setCurrentPage(p)} key={index}>
            {p}
          </a>
        );
      })}
      
  </div>
  
      <ProductsSection data={data} loading={loading} currentPage={currentPage}/>
    </div>
  );
}

export default App;
