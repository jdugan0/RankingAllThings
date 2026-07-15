async function load_movies() {
  document.getElementById('movie_file').click();
}
async function handle_movie_file(files) {
  if (!files || files.length === 0) return;
  const file = files[0];
  //   const csvString = await file.text();
  Papa.parse(file, {
    header: true,
    skipEmptyLines: true,
    complete: function(results) {
      const names = results.data.map(row => row['Name']);
      console.log(names);
    }
  });
  document.getElementById('upload').remove();
}
