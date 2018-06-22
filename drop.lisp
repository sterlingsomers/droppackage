;;; Version Notes: renamed to starcraft from starcrat
;;; A1rev3: Added a second production that /should/ repond to imaginal bufferings.  It doesn't fire yet.
;;; A1rev2: Modified to receive a response
;;; - reduced the number of cycles to 1000
;;; A1rev1: just a loop model. Does not receive a response




;; Define the ACT-R model. This will generate a pair of warnings about slots in the goal
;; buffer not being accessed from productions; these may be ignored.

(clear-all)
(require-extra "blending")
(define-model drop-package


(sgp :esc t    ;;set to t to use subsymbolic computations
     :sim-hook "similarity_function" 
     ;:cache-sim-hook-results t
     ;:bln t    ;;added this to ensure blending was enabled, but not sure if it is actually doing anything...
     ;;some parameters moved from +actr-parameters+ in swarm model
     :ans nil;0.25 ;;activation noise, default is nil, swarm was .75 (M-turkers), Christian recommended .25 as a start.
     :tmp nil  ;;decouple noise if not nil, swarm was .7, perhaps change later.
     :mp 1   ;;partial matching enabled, default is off/nil, start high (2.5 is really high) and move to 1.
     :bll nil;0.5  ;;base-level learning enabled, default is off, this is the recommended value.
     :rt -1.0 ;;retrieval threshold, default is 0, think about editing this number.
     :blc 0;5    ;;base-level learning constant, default is 0, think about editing this number.
     :lf 0.25  ;;latency factor for retrieval times, default is 1.0, think about editing this number.
     :ol nil   ;;affects which base-level learning equation is used, default is nil; use 1 later maybe
     :md -2.5  ;;maximum difference, default similarity value between chunks, default is 1.0, maybe edit this.
     :ga 0.0   ;;set goal activation to 0.0 for spreading activation
     ;:imaginal-activation 1.0 ;;set imaginal activation to 0.0 for spreading activation
     ;:mas 1.0 ;;spreading activation
     ;;back to some parameters in the original sgp here
     :v t      ;;set to nil to turn off model output
     :blt t    ;;set to nil to turn off blending trace
     :trace-detail high ;;lower this as needed, start at high for initial debugging.
     :style-warnings t  ;;set to nil to turn off production warnings, start at t for initial debugging.
     ) ;;end sgp


(chunk-type initialize state)
(chunk-type drop_point pos_x_lon pos_y_lat altitude
            distance_to_hiker altitude_change drop_payload
            trees grass altitude_0 altitude_1 altitude_2
            altitude_3)
(chunk-type observation altitude altitude_change drop_payload
            trees grass altitude_0 altitude_1 altitude_2)

(add-dm
 (goal isa initialize state select-army)
 ;(select-orange isa action value select-orange)
 ;(select-green isa action value select-green)
 (select-beacon isa action value select-beacon)
 (select-around isa action value select-around))
;;chunks defined in Python and vector have random elements

(p p1
     =imaginal>
       ;pos_x =x
       ;pos_y =y
       altitude =alt
       ;distance_to_hiker =distance
       trees =num_trees
       grass =num_grass
       altitude_0 =num_alt0
       altitude_1 =num_alt1
       altitude_2 =num_alt2
       altitude_3 =num_alt3
     ?blending>
       state free
       buffer empty
       error nil
     ==>
     @imaginal>
     +blending>
       altitude =alt
       ;distance_to_hiker =distance
       trees =num_trees
       grass =num_grass
       altitude_0 =num_alt0
       altitude_1 =num_alt1
       altitude_2 =num_alt2
       altitude_3 =num_alt3)

  
  (p p2
     =blending>
       pos_x_lon =x
       pos_y_lat =y
       distance_to_hiker =distance
     ?blending>
       state free
     ==>
     ;!output! (blended value is =val)
     
     ; Overwrite the blended chunk to erase it and keep it 
     ; from being added to dm.  Not necessary, but keeps the 
     ; examples simpler.
     
     ;@blending>    
     
     ;;+blending>
     ;;  isa target
     ;;  key key-2)
     )
  )


