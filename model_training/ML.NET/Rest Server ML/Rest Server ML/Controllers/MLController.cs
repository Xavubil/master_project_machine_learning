using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Rest_Server_ML;

namespace Rest_Server_ML.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class MLController : ControllerBase
    {
        // GET: api/ML    --> train
        [HttpGet]
        public string Get()
        {
            MLClass.train();

            return "trained" ;
        }

        // GET: api/ML/5
        [HttpGet("{id}", Name = "Get")]
        public string Get(int id)
        {
           
            return "true";
        }

        // POST: api/ML    --> predict
        [HttpPost]
        public bool Post([FromBody] string value)
        {
            DataFormat dataToPredict = new DataFormat();
            dataToPredict.featureVector = new float[] { -1.10201144f, 311.261322f, 180.652863f, 0.5f, 317.466675f, 2f, 1f, 1.75f, 0.8333333f, 86.5f, -303.5181f, 18.0625f };
            //dataToPredict.label = true;

            return MLClass.predict(dataToPredict);

        }

        // PUT: api/ML/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody] string value)
        {
        }

        // DELETE: api/ApiWithActions/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {

        }
    }
}
