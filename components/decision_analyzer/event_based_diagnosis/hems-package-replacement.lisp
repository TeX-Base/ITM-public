(defpackage :hems
  (:use #:cl)
  (:import-from #:alexandria
		#:shuffle)
  (:export 
        #:episode-buffer* #:eltm* #:push-to-ep-buffer #:eltm-to-pdf #:test-fun #:compile-program 
        #:test-compiler #:remember #:compute-cpd-concentration #:compile-program-from-file 
        #:get-eltm #:log-message #:rule-based-cpd-singleton-p))

(in-package :hems)