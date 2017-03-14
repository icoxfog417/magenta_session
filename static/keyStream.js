var KeyStream = (function(){
    function KeyStream() {
        this.noteOns = {};
        this.notePlays = [];
        this._start = null;
    }
    KeyStream.prototype.in = function (event) {
        if(this._start == null){
            this._start = new Date();
        }
        if(event.data[0] == 0xFE){
            return 0; // avoid active sensing
        }else if(event.data.length == 3){
            var operation = event.data[0];
            var code = event.data[1];
            var velocity = event.data[2];
            this.record(operation, code, velocity);
        }
    };
    KeyStream.prototype.record = function(operation, code, velocity){
        if(operation == 0x90){//note on
            if(code in this.noteOns){
                this.off(code);
            }else{
                this.noteOns[code] = new Date();
            }
        }else if(operation == 0x80){//note off
            this.off(code);
        }
    }
    KeyStream.prototype.off = function(code){
        if(code in this.noteOns){
            var start = (this.noteOns[code] - this._start) / 1000;
            var duration = (new Date() - this.noteOns[code]) / 1000;
            var np = new NotePlay(code, start ,duration);
            this.notePlays.push(np);
        }
    }
    KeyStream.prototype.toTrack = function(patch){
        var midi = MidiConvert.create();
        var patch = patch === undefined ? 32 : patch;
        var track = midi.track().patch(patch);
        for(var i = 0; i < this.notePlays.length; i++){
            var np = this.notePlays[i];
            track.note(np.code, np.start, np.duration);
        }
        this.reset()
        return midi;
    }
    KeyStream.prototype.reset = function(){
        this.noteOns = {};
        this.notePlays = [];
        this._start = null;
    }

    return KeyStream;
}());

var NotePlay = (function () {
    function NotePlay(code, start, duration) {
        this.code = code;
        this.start = start;
        this.duration = duration;
    }
    return NotePlay;
}());