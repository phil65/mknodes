from __future__ import annotations

from mknodes.cssclasses import cssclasses


GLOBAL = """
.progress-label {
  position: absolute;
  text-align: center;
  font-weight: 700;
  width: 100%;
  margin: 0;
  line-height: 1.2rem;
  white-space: nowrap;
  overflow: hidden;
}

.progress-bar {
  height: 1.2rem;
  float: left;
  background-color: #2979ff;
}


.progress {
  display: block;
  width: 100%;
  margin: 0.5rem 0;
  height: 1.2rem;
  background-color: #eeeeee;
  position: relative;
}

.progress-100plus .progress-bar {
  background-color: #00e676;
}

.progress-80plus .progress-bar {
  background-color: #fbc02d;
}

.progress-60plus .progress-bar {
  background-color: #ff9100;
}

.progress-40plus .progress-bar {
  background-color: #ff5252;
}

.progress-20plus .progress-bar {
  background-color: #ff1744;
}

.progress-0plus .progress-bar {
  background-color: #f50057;
}

"""

THIN = """

.progress.thin {
  margin-top: 0.9rem;
  height: 0.4rem;
}

.progress.thin .progress-label {
  margin-top: -0.4rem;
}

.progress.thin .progress-bar {
  height: 0.4rem;
}
"""


CANDYSTRIPE = """

/* Progress Bars */
.progress.candystripe {
  display: block;
  margin: 10px 0;
  height: 24px;
  -webkit-border-radius: 3px;
  -moz-border-radius: 3px;
  border-radius: 3px;
  background-color: #ededed;
  position: relative;
  box-shadow: inset -1px 1px 3px rgba(0, 0, 0, .1);
}

.progress.candystripe .progress-label {
  position: absolute;
  text-align: center;
  font-weight: bold;
  width: 100%; margin: 0;
  line-height: 24px !important;
  color: #333;
  text-shadow: 1px 1px 0 #fefefe, -1px -1px 0 #fefefe, -1px 1px 0 #fefefe, 1px -1px 0 #fefefe, 0 1px 0 #fefefe, 0 -1px 0 #fefefe, 1px 0 0 #fefefe, -1px 0 0 #fefefe, 1px 1px 2px #000;
  -webkit-font-smoothing: antialiased !important;
  white-space: nowrap;
  overflow: hidden;
}

.progress.candystripe .progress-bar {
  height: 24px;
  float: left;
  -webkit-border-radius: 3px;
  -moz-border-radius: 3px;
  border-radius: 3px;
  background-color: #96c6d7;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .5), inset 0 -1px 0 rgba(0, 0, 0, .1);
  background-size: 30px 30px;
  background-image: -webkit-linear-gradient(
    135deg, rgba(255, 255, 255, .4) 27%,
    transparent 27%,
    transparent 52%, rgba(255, 255, 255, .4) 52%,
    rgba(255, 255, 255, .4) 77%,
    transparent 77%, transparent
  );
  background-image: -moz-linear-gradient(
    135deg,
    rgba(255, 255, 255, .4) 27%, transparent 27%,
    transparent 52%, rgba(255, 255, 255, .4) 52%,
    rgba(255, 255, 255, .4) 77%, transparent 77%,
    transparent
  );
  background-image: -ms-linear-gradient(
    135deg,
    rgba(255, 255, 255, .4) 27%, transparent 27%,
    transparent 52%, rgba(255, 255, 255, .4) 52%,
    rgba(255, 255, 255, .4) 77%, transparent 77%,
    transparent
  );
  background-image: -o-linear-gradient(
    135deg,
    rgba(255, 255, 255, .4) 27%, transparent 27%,
    transparent 52%, rgba(255, 255, 255, .4) 52%,
    rgba(255, 255, 255, .4) 77%, transparent 77%,
    transparent
  );
  background-image: linear-gradient(
    135deg,
    rgba(255, 255, 255, .4) 27%, transparent 27%,
    transparent 52%, rgba(255, 255, 255, .4) 52%,
    rgba(255, 255, 255, .4) 77%, transparent 77%,
    transparent
  );
}
"""  # noqa: E501

CANDYSTRIPE_ANIMATED = """
.candystripe-animate .progress-bar{
  -webkit-animation: animate-stripes 3s linear infinite;
  -moz-animation: animate-stripes 3s linear infinite;
  animation: animate-stripes 3s linear infinite;
}

@-webkit-keyframes animate-stripes {
  0% {
    background-position: 0 0;
  }

  100% {
    background-position: 60px 0;
  }
}

@-moz-keyframes animate-stripes {
  0% {
    background-position: 0 0;
  }

  100% {
    background-position: 60px 0;
  }
}

@keyframes animate-stripes {
  0% {
    background-position: 0 0;
  }

  100% {
    background-position: 60px 0;
  }
}

"""


class ProgressBarCSS(cssclasses.CSS):
    PREFIX = ".progress"

    def __init__(self):
        super().__init__(GLOBAL)

    def set_height(self, height: int | str):
        height_str = f"{height}px" if isinstance(height, int) else height
        self[self.PREFIX]["height"] = height_str
        self[f"{self.PREFIX}-label"]["line-height"] = height_str
        self[f"{self.PREFIX}-bar"]["height"] = height_str


class CandyStripeCSS(cssclasses.CSS):
    PREFIX = ".progress.candystripe"

    def __init__(self):
        super().__init__(CANDYSTRIPE)

    def set_height(self, height: int | str):
        height_str = f"{height}px" if isinstance(height, int) else height
        self[self.PREFIX]["height"] = height_str
        self[f"{self.PREFIX} .progress-label"]["line-height"] = (height_str, "important")
        self[f"{self.PREFIX} .progress-bar"]["height"] = height_str


class AnimatedCandyStripeCSS(CandyStripeCSS):
    def __init__(self):
        cssclasses.CSS.__init__(self, CANDYSTRIPE + CANDYSTRIPE_ANIMATED)


if __name__ == "__main__":
    ss = ProgressBarCSS()
    ss.set_height("1.2rem")
    print(ss)
