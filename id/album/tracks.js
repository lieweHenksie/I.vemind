// The album, in one place. BOTH the hallway (index.html) and the reading room (essay.html)
// read this file, so a track can never exist in one and not the other.
//   src   — the song folder, relative to id/album/
//   essay — the source writing: mycelium/essays/<essay>.md  (agar-lab's is still 'essay-1')
// The intermezzos are named for the line they carry, not numbered — insert another one and
// nothing has to be renamed.
window.ALBUM = {
  band: "I'VEMIND",
  title: 'tough times ever last, tough people never do',
  tracks: [
    { src: '../demi_demi/',           essay: 'demi_demi',           name: 'demi demi',      sub: 'trance · crate jam' },
    { src: '../hes-wrong-of-course/', essay: 'hes-wrong-of-course', name: 'intermezzo',     sub: "he's wrong of course · toward the ward" },
    { src: '../theGodInUrhead/',      essay: 'theGodInUrhead',      name: 'theGodInUrhead', sub: 'cinematic downtempo' },
    { src: '../nature-was-a-gift/',   essay: 'nature-was-a-gift',   name: 'intermezzo',     sub: 'nature was a gift once · toward the meadow' },
    { src: '../nice_ron/',            essay: 'nice_ron',            name: 'nice ron',       sub: '8-bit melodic techno · crate jam' },
    { src: '../all-good-things/',     essay: 'all-good-things',     name: 'intermezzo',     sub: 'all good things · toward the lab' },
    { src: '../agar-lab/',            essay: 'essay-1',             name: 'essay-1',        sub: 'the agar lab · techno' },
    { src: '../oh_dear/',             essay: 'oh_dear',             name: 'oh dear',        sub: 'dub techno requiem' },
  ],
};
