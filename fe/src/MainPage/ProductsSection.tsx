import React from "react";
import styles from "./App.module.css";
import { data } from "../utils/models";
import { Link, useNavigate } from 'react-router-dom';

function ProductsSection({ data,loading,currentPage }: { data: data[],loading:boolean,currentPage:number }) {
  

  return (
    <div className={styles["content-section"]}>
      {loading && <div className={styles.loader}></div>}
      {data.slice((currentPage-1)*8,(currentPage-1)*8+8).map((product, index) => {
        
        return (
          <a href={product.link} target="_blank" rel="noopener noreferrer" className={styles["card-item"]}>
          <div className={styles["img-container"]}>
              {product.stockOut &&<div className={styles.stock_out}>STOCK OUT</div>}
              {product.image ? (
                <img src={product.image} alt={product.name} />
              ) : (
                <i className={`bi bi-image ${styles['bi-image']}`}></i>
              )}
            </div>
            <div className={styles["item-info"]}>
              <h3>{product.name}</h3>
              <h2>{product.shop}</h2>
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
