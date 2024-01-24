class TimeLock {
    constructor(time, submit_btn) {
        this.locked = true;
        this.time = time;
        this.submit_btn = $(submit_btn);
        this.id = setInterval(this.time_counter.bind(this), 1000);
    }

    get is_locked() {
        return this.locked;
    }

    time_counter() {
        // console.log(this.time);
        this.time -= 1;
        if (this.time == 0) {
            this.locked = false;
            clearInterval(this.id);
            this.submit_btn.text("Submit");
            this.submit_btn.attr("disabled", false);
            return;
        }
        this.submit_btn.text("Submit ("+this.time+")");
    }
}

class ReadLock {
    constructor(target_element, warning_element=null, time=50) {
        this.target_element = $(target_element);
        this.locked = true;
        this.target_element.on("scroll", this.check_scroll_bottom.bind(this));
        this.work = true;
        this.time = time;
        if (this.time != false) {
            setInterval(function() {this.work=true}.bind(this), this.time);
        }
        this.warning_element = warning_element;
        this.check_scroll_bottom();
    }

    get is_locked() {
        return this.locked;
    }

    check_scroll_bottom() {
        if (this.work) {
            if (this.time != false) {
                this.work = false;
            }
            //console.log(this.target_element.scrollTop(), this.target_element.height(), this.target_element[0].scrollHeight);
            // Notice that 30 here is the padding size.
            if (this.target_element.scrollTop() + this.target_element.height()+30 >= this.target_element[0].scrollHeight) {
                this.target_element.unbind("scroll");
                this.locked = false;

                if(this.warning_element != null) {
                    this.warning_element.hide();
                }
            }
        }
    }
}
