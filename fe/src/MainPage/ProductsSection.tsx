import React from "react";
import styles from "./App.module.css";
import { data } from "../utils/models";
import { Link, useNavigate } from 'react-router-dom';

function ProductsSection({ data,loading,currentPage }: { data: data[],loading:boolean,currentPage:number }) {
  
const images={
  istore:"https://istore.md/build/assets/istore-logo-DZGDlRVQ.svg",
  maximum:"https://maximum.md/static/projects/maximum.md/dist/images/home/logo.png",
  smart:"https://www.smart.md/catalog/view/smartv3/svg/logo.svg",

}
  return (
    <div className={styles["content-section"]}>
      {loading && <div className={styles.loader}></div>}
      {data.slice((currentPage-1)*8,(currentPage-1)*8+8).map((product, index) => {
        
        return (
          <a key={index} href={product.link} target="_blank" rel="noopener noreferrer" className={styles["card-item"]}>
          <div className={styles["img-container"]}>
              {product.stockOut &&<div className={styles.stock_out}>STOCK OUT</div>}
              {product.image&&product.shop!=="istore.md" ? (
                <img src={product.image} alt={product.name} />
              ) : (
                <i className={`bi bi-image ${styles['bi-image']}`}></i>
              )}
            </div>
            <div className={styles["item-info"]}>
              <h3>{product.name}</h3>
              <h2>{product.shop}</h2>
              {/* <img className={styles.shop} src={product.shop==="darwin"?images.darwin:product.shop==="maximum_md"?images.maximum:product.shop==="smart.md"?images.smart:product.shop==="istore.md"?images.istore:""} alt={product.shop} /> */}
              <div className={styles["price-container"]}>
                <span className={styles["price"]}>{product.price}MDL</span>
             {product.lastPrice!==product.price&&<div className={styles['last-price']}><s>{product.lastPrice}</s></div>}

                {product.discount ? (
                  <div className={styles["discount-container"]}>
                    <span className={styles["discount"]}>
                      -{product.discount} MDL
                    </span>

                  </div>
                ) : null}
              </div>
            </div>
            {/* <p>{product.price}</p> */}
          </a>
        );
      })}
    </div>
  );
}

export default ProductsSection;
