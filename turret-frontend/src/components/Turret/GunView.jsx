export default function GunView({
  image,
  className,
  style
}) {
  return (
    <div className={className} style={style}>
      <img src={image} draggable={false} alt="Gun"/>
    </div>
  )
}
