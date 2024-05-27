import style from './App.module.css'
function ProgressBar({progress}: {progress:number}) {
  return (
    <div className={style['progress-container']}>
        <div style={{width:`${progress*100}%`}} className={style['progress-bar']}></div>
    </div>
  )
}

export default ProgressBar